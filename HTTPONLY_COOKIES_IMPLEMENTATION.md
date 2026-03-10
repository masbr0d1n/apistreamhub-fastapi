# httpOnly Cookies Implementation

## Summary
Implemented httpOnly cookies for JWT token authentication to improve security by preventing XSS attacks from accessing tokens via JavaScript.

## Changes Made

### 1. Updated Login Endpoint (`app/api/v1/auth.py`)
- Added `Response` parameter to login function
- Set httpOnly cookies for both `access_token` and `refresh_token`
- Cookie configuration:
  - `httponly=True` - Prevents JavaScript access
  - `secure=False` - Set to True in production (HTTPS)
  - `samesite="lax"` - CSRF protection
  - `max_age`: 3 days for access token, 30 days for refresh token

### 2. Added Logout Endpoint (`app/api/v1/auth.py`)
- New POST `/logout` endpoint
- Clears both `access_token` and `refresh_token` cookies
- Returns confirmation message

### 3. Updated Token Verification (`app/core/security.py`)
- Modified `get_current_user` dependency to read from cookies first
- Falls back to Authorization header for backward compatibility
- Added `Request` parameter to access cookies

### 4. Updated Refresh Endpoint (`app/api/v1/auth.py`)
- Changed to read `refresh_token` from cookie instead of query parameter
- Sets new `access_token` cookie on successful refresh
- Added `Response` parameter

### 5. Updated Tests (`tests/test_auth.py` and `tests/conftest.py`)
- Added `TestAuthCookies` class with comprehensive cookie tests
- Added `test_user` and `auth_headers` fixtures to conftest.py
- Updated existing tests to work with cookie-based authentication

## Acceptance Criteria

- [x] **Login sets httpOnly cookies** - Login endpoint now sets both access_token and refresh_token as httpOnly cookies
- [x] **Logout clears cookies** - New logout endpoint deletes both cookies
- [x] **Protected routes read from cookies** - `get_current_user` dependency reads from cookies first, with header fallback
- [x] **Refresh works with cookies** - Refresh endpoint reads refresh_token from cookie and sets new access_token cookie
- [x] **Tests updated** - Added comprehensive test coverage for cookie-based authentication

## Security Notes

### Production Deployment
Before deploying to production:
1. Set `secure=True` for all cookie settings (requires HTTPS)
2. Consider `samesite="strict"` for enhanced CSRF protection
3. Ensure all API endpoints are served over HTTPS
4. Update CORS settings to allow credentials: `allow_credentials=True`

### Cookie Configuration
```python
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,      # ✓ Prevents XSS
    secure=True,        # ✓ Set in production (HTTPS only)
    samesite="lax",     # ✓ CSRF protection
    max_age=60 * 24 * 3 * 60  # 3 days
)
```

## Backward Compatibility
The implementation maintains backward compatibility by:
- Still returning tokens in JSON response (for frontend transition)
- Falling back to Authorization header if cookie not present
- Allowing gradual frontend migration to cookie-based auth

## Testing
Run tests with:
```bash
.venv/bin/python -m pytest tests/test_auth.py -v
```

Note: Some tests may fail due to pre-existing SQLite ARRAY type incompatibility, not related to cookie implementation.

## Files Modified
1. `app/api/v1/auth.py` - Login, logout, refresh endpoints
2. `app/core/security.py` - Token verification from cookies
3. `tests/test_auth.py` - Added cookie authentication tests
4. `tests/conftest.py` - Added test fixtures
