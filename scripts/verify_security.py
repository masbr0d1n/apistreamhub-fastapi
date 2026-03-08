#!/usr/bin/env python3
"""
Security verification script for StreamHub API.
Run this to verify all security hardening features are working.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_jwt_secret():
    """Test JWT secret configuration."""
    print("\n🔐 Testing JWT Secret Configuration...")
    
    try:
        from app.config import settings
        
        # Check if secret is set
        if not settings.JWT_SECRET_KEY:
            print("  ❌ FAIL: JWT_SECRET_KEY is not set")
            return False
        
        # Check length
        if len(settings.JWT_SECRET_KEY) < 32:
            print(f"  ❌ FAIL: JWT_SECRET_KEY is too short ({len(settings.JWT_SECRET_KEY)} chars, need 32+)")
            return False
        
        # Check for weak secrets
        weak_secrets = [
            "your-secret-key-change-in-production",
            "test-secret-key-change-in-production",
            "secret",
            "changeme",
            "test"
        ]
        
        if settings.JWT_SECRET_KEY.lower() in weak_secrets:
            print("  ❌ FAIL: JWT_SECRET_KEY is using a weak/default value")
            return False
        
        print(f"  ✅ PASS: JWT secret is properly configured ({len(settings.JWT_SECRET_KEY)} characters)")
        return True
        
    except Exception as e:
        print(f"  ❌ FAIL: {str(e)}")
        return False


def test_rate_limiter():
    """Test rate limiter configuration."""
    print("\n⏱️  Testing Rate Limiter Configuration...")
    
    try:
        from app.core.rate_limiter import limiter, RATE_LIMITS
        
        # Check limiter exists
        if not limiter:
            print("  ❌ FAIL: Rate limiter not configured")
            return False
        
        # Check rate limits
        expected_limits = {
            "auth_login": "5/minute",
            "auth_register": "3/minute",
            "video_upload": "10/minute",
            "default": "60/minute"
        }
        
        for endpoint, expected in expected_limits.items():
            if RATE_LIMITS.get(endpoint) != expected:
                print(f"  ❌ FAIL: Rate limit for {endpoint} is incorrect")
                return False
        
        print("  ✅ PASS: Rate limiter is properly configured")
        print(f"    - Login: {RATE_LIMITS['auth_login']}")
        print(f"    - Register: {RATE_LIMITS['auth_register']}")
        print(f"    - Video Upload: {RATE_LIMITS['video_upload']}")
        print(f"    - Default: {RATE_LIMITS['default']}")
        return True
        
    except Exception as e:
        print(f"  ❌ FAIL: {str(e)}")
        return False


def test_env_example():
    """Test .env.example file."""
    print("\n📄 Testing .env.example Documentation...")
    
    try:
        env_example_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            '.env.example'
        )
        
        if not os.path.exists(env_example_path):
            print("  ❌ FAIL: .env.example file not found")
            return False
        
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        # Check for required documentation
        required = [
            'JWT_SECRET_KEY',
            'python -c',
            'secrets.token_urlsafe',
            '32 characters'
        ]
        
        for req in required:
            if req not in content:
                print(f"  ❌ FAIL: .env.example missing documentation for: {req}")
                return False
        
        print("  ✅ PASS: .env.example is properly documented")
        return True
        
    except Exception as e:
        print(f"  ❌ FAIL: {str(e)}")
        return False


def test_app_integration():
    """Test that app loads with security features."""
    print("\n🚀 Testing Application Integration...")
    
    try:
        from app.main import app
        
        # Check rate limiter is registered
        if not hasattr(app.state, 'limiter'):
            print("  ❌ FAIL: Rate limiter not registered with app")
            return False
        
        # Check exception handler
        handlers = app.exception_handlers
        if 429 not in handlers:
            print("  ❌ FAIL: Rate limit exception handler not registered")
            return False
        
        print("  ✅ PASS: Application properly configured with security features")
        return True
        
    except Exception as e:
        print(f"  ❌ FAIL: {str(e)}")
        return False


def main():
    """Run all security verification tests."""
    print("=" * 60)
    print("🛡️  StreamHub API - Security Verification")
    print("=" * 60)
    
    tests = [
        test_jwt_secret,
        test_rate_limiter,
        test_env_example,
        test_app_integration
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✅ All security features are properly configured!")
        print("\n📝 Next steps:")
        print("   1. Generate production JWT secret:")
        print("      python -c 'import secrets; print(secrets.token_urlsafe(32))'")
        print("   2. Update .env file with the new secret")
        print("   3. Deploy to production")
        print("   4. Monitor 429 responses in logs")
        return 0
    else:
        print("\n❌ Some security features are not properly configured!")
        print("   Please review the failures above and fix them.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
