# ----------------------------
# Stage 1: Builder
# ----------------------------
FROM python:3.14-slim AS builder

WORKDIR /app

RUN pip install uv --no-cache-dir

COPY pyproject.toml uv.lock ./
COPY sv_mcp/ ./sv_mcp/

RUN uv sync --no-dev --frozen

# ----------------------------
# Stage 2: Runtime
# ----------------------------
FROM python:3.14-slim AS runtime

LABEL io.modelcontextprotocol.server.name="io.github.blazemeter/sv-mcp"

ENV MCP_DOCKER=true
ENV PYTHONDONTWRITEBYTECODE=1
# Telemetry defaults to the Perforce gRPC collector. Override the destination
# with OTEL_EXPORTER_OTLP_ENDPOINT, or set OTEL_SDK_DISABLED=true to turn it off.

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

RUN groupadd -r sv-mcp && useradd -r -g sv-mcp sv-mcp
USER sv-mcp

ENTRYPOINT ["sv-mcp"]
CMD []
