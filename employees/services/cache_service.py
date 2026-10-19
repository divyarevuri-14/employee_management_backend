
import logging

from django.core.cache import cache
from django.db.models import Count

logger = logging.getLogger("employees")

CACHE_KEY = "employee:department_summary:v1"
CACHE_TIMEOUT = 300


def get_department_employee_summary():
    """Return department summary, using the database if caching fails."""
    cached_data = None

    # Try reading from cache. Redis may be unavailable.
    try:
        cached_data = cache.get(CACHE_KEY)
    except Exception:
        logger.exception("Department summary cache read failed")

    if cached_data is not None:
        logger.info("Department summary cache HIT")
        return cached_data

    logger.info("Department summary cache MISS")

    from employees.models import Employee

    summary = list(
        Employee.objects
        .values("department_fk__name")
        .annotate(employee_count=Count("id"))
        .order_by("department_fk__name")
    )

    # Return the database result even if Redis write fails.
    try:
        cache.set(CACHE_KEY, summary, timeout=CACHE_TIMEOUT)
        logger.info("Department summary cached successfully")
    except Exception:
        logger.exception("Department summary cache write failed")

    return summary


def invalidate_department_employee_summary():
    """Invalidate cached department statistics after employee changes."""
    try:
        cache.delete(CACHE_KEY)
        logger.info("Department summary cache invalidated")
    except Exception:
        logger.exception("Department summary cache invalidation failed")
