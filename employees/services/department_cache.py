import logging

from django.core.cache import cache
from django.db.models import Count

from employees.models import Employee

logger = logging.getLogger(__name__)

DEPARTMENT_SUMMARY_KEY = "department_employee_summary"
CACHE_TIMEOUT = 300


def get_department_employee_summary():
    # 1. Try to read from Redis cache
    try:
        cached_data = cache.get(DEPARTMENT_SUMMARY_KEY)

        if cached_data is not None:
            logger.info("Department summary cache HIT")
            return cached_data

    except Exception:
        logger.exception("Cache read failed; fetching from database")

    # 2. Cache MISS or Redis failure: fetch fresh data
    data = list(
        Employee.objects
        .values("department_fk__name")
        .annotate(employee_count=Count("id"))
        .order_by("department_fk__name")
    )

    # 3. Try to store the fresh result in cache
    try:
        cache.set(
            DEPARTMENT_SUMMARY_KEY,
            data,
            timeout=CACHE_TIMEOUT,
        )
        logger.info("Department summary cache updated")

    except Exception:
        logger.exception("Cache write failed; returning database result")

    return data


def invalidate_department_employee_summary():
    try:
        cache.delete(DEPARTMENT_SUMMARY_KEY)
        logger.info("Department summary cache invalidated")

    except Exception:
        logger.exception("Cache invalidation failed")