"""
FFmpeg Service - Video thumbnail generation and metadata extraction
Using subprocess with scale filter (FIXED - more reliable)
"""
import subprocess
import json
import base64
import os
from pathlib import Path
from typing import Dict, Any, Optional


class FFmpegService:
    """Service for video processing using FFmpeg"""
    
    def __init__(self, upload_dir: str = None):
        import os
        if upload_dir is None:
            upload_dir = str(Path(os.getcwd()) / "uploads" / "videos")
        self.upload_dir = Path(upload_dir)
        self.thumbnail_dir = self.upload_dir.parent / "thumbnails"
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_thumbnail(
        self,
        video_path: str,
        timestamp: float = 1.0,
        width: int = 320
    ) -> Optional[str]:
        """
        Generate thumbnail from video at specified timestamp using scale filter
        
        Args:
            video_path: Path to video file
            timestamp: Time position for thumbnail (seconds)
            width: Thumbnail width in pixels (height auto-calculated)
            
        Returns:
            Base64 encoded thumbnail image or None
        """
        try:
            video_filename = Path(video_path).stem
            thumbnail_path = self.thumbnail_dir / f"{video_filename}_thumb.jpg"
            
            # Generate thumbnail using FFmpeg with scale filter (more reliable)
            # Using -vf "scale=320:-1" instead of -s "320x-1"
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", str(timestamp),
                "-vframes", "1",
                "-vf", f"scale={width}:-1",  # Use scale filter instead of -s
                "-y",  # Overwrite if exists
                str(thumbnail_path)
            ]
            
            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                check=False
            )
            
            if result.returncode == 0 and thumbnail_path.exists():
                # Success - read file and convert to base64
                with open(thumbnail_path, 'rb') as f:
                    thumbnail_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                # Clean up thumbnail file
                thumbnail_path.unlink()
                
                print(f"✓ Thumbnail generated: {len(thumbnail_base64)} chars")
                return thumbnail_base64
                
            else:
                # FFmpeg failed
                stderr_output = result.stderr.decode('utf-8', errors='ignore')
                print(f"✗ FFmpeg thumbnail failed (code {result.returncode})")
                print(f"  Command: {' '.join(cmd)}")
                print(f"  STDERR: {stderr_output[:500]}...")
                return None
                
        except subprocess.TimeoutExpired:
            print("✗ FFmpeg thumbnail generation timed out")
            return None
        except Exception as e:
            print(f"✗ Error generating thumbnail: {e}")
            return None
    
    def extract_metadata(self, video_path: str) -> Dict[str, Any]:
        """
        Extract video metadata using ffprobe
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing video metadata
        """
        try:
            # Use ffprobe to get JSON metadata
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                check=True,
                text=True
            )
            
            probe = json.loads(result.stdout)
            
            metadata = {
                'duration': float(probe['format'].get('duration', 0)),
                'size': int(probe['format'].get('size', 0)),
                'bitrate': int(probe['format'].get('bit_rate', 0)) if 'bit_rate' in probe['format'] else None,
            }
            
            # Extract video stream metadata
            video_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'video'),
                None
            )
            
            if video_stream:
                # Calculate FPS from r_frame_rate (e.g., "30000/1001")
                fps_str = video_stream.get('r_frame_rate', '0/1')
                try:
                    num, den = fps_str.split('/')
                    fps = int(num) / int(den) if int(den) > 0 else 0
                except:
                    fps = 0
                
                metadata.update({
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'fps': round(fps, 2),
                    'video_codec': video_stream.get('codec_name', ''),
                    'video_codec_desc': video_stream.get('codec_long_name', ''),
                })
            
            # Extract audio stream metadata
            audio_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'audio'),
                None
            )
            
            if audio_stream:
                metadata.update({
                    'audio_codec': audio_stream.get('codec_name', ''),
                    'audio_codec_desc': audio_stream.get('codec_long_name', ''),
                    'audio_sample_rate': int(audio_stream.get('sample_rate', 0)) if 'sample_rate' in audio_stream else None,
                    'audio_channels': int(audio_stream.get('channels', 0)) if 'channels' in audio_stream else None,
                })
            
            print(f"✓ Metadata extracted: {metadata.get('width')}x{metadata.get('height')} @ {metadata.get('fps')} fps")
            return metadata
            
        except subprocess.TimeoutExpired:
            print("✗ Metadata extraction timed out")
            return self._get_default_metadata()
        except Exception as e:
            print(f"✗ Error extracting metadata: {e}")
            return self._get_default_metadata()
    
    def _get_default_metadata(self) -> Dict[str, Any]:
        """Return default metadata when extraction fails"""
        return {
            'duration': 0,
            'width': 0,
            'height': 0,
            'fps': 0,
            'bitrate': 0,
            'video_codec': '',
            'audio_codec': '',
        }
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get complete video information (thumbnail + metadata)
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with thumbnail and metadata
        """
        metadata = self.extract_metadata(video_path)
        thumbnail = self.generate_thumbnail(video_path)
        
        return {
            'thumbnail_data': thumbnail,
            **metadata
        }


# Singleton instance
ffmpeg_service = FFmpegService()
