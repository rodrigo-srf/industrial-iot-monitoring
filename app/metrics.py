from time import perf_counter

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest


HTTP_REQUESTS = Counter(
    "industrial_http_requests_total",
    "Total HTTP requests handled by the API.",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION = Histogram(
    "industrial_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "path"],
)


def install_metrics(app: FastAPI) -> None:
    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        started = perf_counter()
        response = await call_next(request)
        elapsed = perf_counter() - started

        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)

        HTTP_REQUESTS.labels(
            method=request.method,
            path=path,
            status=str(response.status_code),
        ).inc()

        HTTP_REQUEST_DURATION.labels(
            method=request.method,
            path=path,
        ).observe(elapsed)

        return response

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
