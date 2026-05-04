# Issues pendientes para Inventory_Sales

## 1. Security: Set DEBUG=False for production
**Labels:** security, production
**Description:**
Current settings have DEBUG=True which exposes sensitive information including stack traces, environment variables, and SQL queries. Need to ensure DEBUG is set to False via environment variable `DJANGO_DEBUG=false` for production deployments.

## 2. Security: Enable SSL/HTTPS in production
**Labels:** security, production
**Description:**
- `SECURE_SSL_REDIRECT` should be True in production
- `SESSION_COOKIE_SECURE` should be True
- `CSRF_COOKIE_SECURE` should be True
These settings should be controlled via environment variables.

## 3. Enhancement: Add automated tests
**Labels:** enhancement, testing
**Description:**
Currently no automated tests are configured. Need to add:
- Unit tests for models
- Integration tests for views
- Security tests for authentication and CSRF
- Use pytest-django or Django's test framework

## 4. Enhancement: Optimize database queries
**Labels:** performance, enhancement
**Description:**
- Review and optimize queryset usage (add `select_related` and `prefetch_related` where needed)
- Add database indexes for frequently queried fields
- Monitor and optimize slow queries

## 5. Enhancement: Add input validation and sanitization
**Labels:** security, enhancement
**Description:**
- Review all forms for proper validation
- Add server-side validation for all inputs
- Sanitize user inputs to prevent XSS and injection attacks
- Review file upload handling for security

## 6. Enhancement: Implement proper error pages
**Labels:** enhancement, ui
**Description:**
- Create custom 400, 403, 404, 500 error pages
- Ensure error pages work in both light and dark themes
- Add user-friendly messages for each error type

## 7. Security: Review and harden Django settings
**Labels:** security
**Description:**
- Review all security-related settings
- Consider adding `SECURE_CONTENT_TYPE_NOSNIFF = True`
- Consider adding `X_CONTENT_TYPE_OPTIONS = 'nosniff'`
- Review CORS and CSRF settings for API endpoints

## 8. Enhancement: Add logging and monitoring
**Labels:** enhancement, monitoring
**Description:**
- Implement structured logging
- Add Sentry or similar for error tracking
- Add performance monitoring
- Log security-related events (failed logins, etc.)
