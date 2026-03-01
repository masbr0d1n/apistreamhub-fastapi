"""
Video Upload Utilities
Handles video file processing with FFmpeg
"""

import os
import subprocess
import json
from typing import Dict, Optional, Tuple
from pathlib import Path


class VideoProcessor:
    """Process video files using FFmpeg"""

    def __init__(self, upload_dir: str = "/app/uploads/videos"):
        self.upload_dir = Path(upload_dir)
        self.thumbnail_dir = self.upload_dir / "thumbnails"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)

    async def process_video(
        self,
        file_path: str,
        filename: str
    ) -> Dict:
        """
        Process uploaded video file

        Args:
            file_path: Path to uploaded video file
            filename: Original filename

        Returns:
            Dictionary with video metadata:
            - thumbnail_path: Path to extracted thumbnail
            - duration: Video duration in seconds
            - width: Video width
            - height: Video height
            - video_codec: Video codec
            - video_bitrate: Video bitrate
            - audio_codec: Audio codec
            - audio_bitrate: Audio bitrate
            - fps: Frames per second
        """
        try:
            # Get video info using ffprobe
            info = await self._get_video_info(file_path)

            # Validate minimum resolution (480p)
            if info['height'] < 480:
                raise ValueError(
                    f"Video resolution must be at least 480p. "
                    f"Current resolution: {info['width']}x{info['height']}"
                )

            # Extract thumbnail
            thumbnail_filename = f"{Path(filename).stem}_thumb.jpg"
            thumbnail_path = str(self.thumbnail_dir / thumbnail_filename)
            await self._extract_thumbnail(file_path, thumbnail_path)

            # Return processed info
            return {
                'thumbnail_path': thumbnail_path,
                'duration': info['duration'],
                'width': info['width'],
                'height': info['height'],
                'video_codec': info['video_codec'],
                'video_bitrate': info['video_bitrate'],
                'audio_codec': info['audio_codec'],
                'audio_bitrate': info['audio_bitrate'],
                'fps': info['fps'],
                'resolution': f"{info['width']}x{info['height']}",
            }

        except Exception as e:
            raise Exception(f"Failed to process video: {str(e)}")

    async def _get_video_info(self, file_path: str) -> Dict:
        """Get video metadata using ffprobe"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate,codec_name,bit_rate',
            '-show_entries', 'format=duration',
            '-of', 'json',
            file_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            metadata = json.loads(result.stdout)

            stream = metadata['streams'][0]
            format_info = metadata['format']

            # Calculate FPS
            fps_str = stream.get('r_frame_rate', '25/1')
            fps_num, fps_den = map(int, fps_str.split('/'))
            fps = fps_num / fps_den

            # Get audio info
            audio_cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'a:0',
                '-show_entries', 'stream=codec_name,bit_rate',
                '-of', 'json',
                file_path
            ]

            audio_result = subprocess.run(audio_cmd, capture_output=True, text=True)
            audio_data = json.loads(audio_result.stdout)

            audio_codec = None
            audio_bitrate = None
            if audio_data.get('streams'):
                audio_stream = audio_data['streams'][0]
                audio_codec = audio_stream.get('codec_name')
                audio_bitrate = int(audio_stream.get('bit_rate', 0)) if audio_stream.get('bit_rate') else None

            return {
                'width': int(stream['width']),
                'height': int(stream['height']),
                'duration': float(format_info['duration']),
                'video_codec': stream['codec_name'],
                'video_bitrate': int(stream['bit_rate']) if stream.get('bit_rate') else None,
                'audio_codec': audio_codec,
                'audio_bitrate': audio_bitrate,
                'fps': round(fps, 2),
            }

        except subprocess.CalledProcessError as e:
            raise Exception(f"FFprobe failed: {e.stderr}")
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")

    async def _extract_thumbnail(self, video_path: str, output_path: str):
        """Extract thumbnail from video at 50% duration"""
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', '00:00:01.000',  # Take thumbnail at 1 second
            '-vframes', '1',
            '-vf', 'scale=320:180',  # Thumbnail resolution
            '-y',
            output_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg thumbnail extraction failed: {e.stderr}")

    def get_video_specs_text(self, metadata: Dict) -> str:
        """Generate human-readable video specs"""
        specs = []

        # Video specs
        specs.append(f"📹 Resolution: {metadata['resolution']}")
        specs.append(f"⏱️ Duration: {self._format_duration(metadata['duration'])}")
        specs.append(f"🎞️ Codec: {metadata['video_codec']}")
        specs.append(f"📊 FPS: {metadata['fps']}")

        if metadata['video_bitrate']:
            specs.append(f"💾 Video Bitrate: {self._format_bitrate(metadata['video_bitrate'])}")

        # Audio specs
        if metadata['audio_codec']:
            specs.append(f"🔊 Audio Codec: {metadata['audio_codec']}")

        if metadata['audio_bitrate']:
            specs.append(f"💾 Audio Bitrate: {self._format_bitrate(metadata['audio_bitrate'])}")

        return '\n'.join(specs)

    def _format_duration(self, seconds: float) -> str:
        """Format duration as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def _format_bitrate(self, bitrate_bps: int) -> str:
        """Format bitrate in human-readable format"""
        bitrate_kbps = bitrate_bps / 1000
        if bitrate_kbps >= 1000:
            return f"{bitrate_kbps/1000:.1f} Mbps"
        else:
            return f"{bitrate_kbps:.0f} kbps"


# Lazy initialization to avoid permission issues at import time
video_processor: Optional[VideoProcessor] = None

def get_video_processor() -> VideoProcessor:
    """Get or create video processor instance."""
    global video_processor
    if video_processor is None:
        video_processor = VideoProcessor()
    return video_processor
