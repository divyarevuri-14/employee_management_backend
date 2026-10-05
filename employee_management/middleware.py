import logging
import time
import uuid

from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.request_id = str(uuid.uuid4())
        request.start_time = time.perf_counter()

        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            username = user.username
        else:
            username = "anonymous"

        logger.info(
            "Request started | request_id=%s | method=%s | path=%s | user=%s",
            request.request_id,
            request.method,
            request.path,
            username,
        )

    def process_response(self, request, response):
        start_time = getattr(request, "start_time", None)
        request_id = getattr(request, "request_id", "unknown")

        if start_time:
            execution_time = time.perf_counter() - start_time
        else:
            execution_time = 0

        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            username = user.username
        else:
            username = "anonymous"

        logger.info(
            "Request completed | request_id=%s | method=%s | path=%s | "
            "user=%s | status=%s | execution_time=%.4fs",
            request_id,
            request.method,
            request.path,
            username,
            response.status_code,
            execution_time,
        )

        response["X-Request-ID"] = request_id

        return response