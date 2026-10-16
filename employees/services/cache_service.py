import logging

from django.core.cache import cache
from django.db.models import Count

logger = logging.getLogger("employees")

# Cache key naming convention
CACHE_KEY = "employee:department_summary:v1"

# Cache validity: 5 minutes
CACHE_TIMEOUT = 300


def get_department_employee_summary():
    """
    Return department-wise employee statistics.

    If cached data exists, return it from Redis.
    Otherwise, fetch data from the database and cache it.
    """

    # Step 1: Check whether data is available in cache
    cached_data = cache.get(CACHE_KEY)

    if cached_data is not None:
        logger.info("Department summary cache HIT")
        return cached_data

    # Step 2: Cache MISS - fetch fresh data
    logger.info("Department summary cache MISS")

    from employees.models import Employee

    summary = list(
        Employee.objects
        .values("department_fk__name")
        .annotate(employee_count=Count("id"))
        .order_by("department_fk__name")
    )

    # Step 3: Store the result in cache for 5 minutes
    cache.set(CACHE_KEY, summary, timeout=CACHE_TIMEOUT)

    logger.info("Department summary cached successfully")

    return summary


def invalidate_department_employee_summary():
    """
    Invalidate cached department statistics after employee data changes.
    """

    cache.delete(CACHE_KEY)

    logger.info("Department summary cache invalidated")
