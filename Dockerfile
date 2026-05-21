# ----------------------------
# Stage 1: Builder
# ----------------------------
FROM python:3.13-slim AS builder

WORKDIR /app

RUN pip install uv --no-cache-dir

COPY pyproject.toml uv.lock ./
COPY sv_mcp/ ./sv_mcp/

RUN uv sync --extra telemetry --no-dev --frozen

# ----------------------------
# Stage 2: Runtime
# ----------------------------
FROM python:3.13-slim AS runtime

ENV MCP_DOCKER=true
ENV OTEL_EXPORTER_OTLP_ENDPOINT=""
ENV OTEL_SDK_DISABLED=""

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

RUN groupadd -r sv-mcp && useradd -r -g sv-mcp sv-mcp
USER sv-mcp

ENTRYPOINT ["sv-mcp"]
CMD []
