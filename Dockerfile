# ----------------------------
# Stage 1: Builder
# ----------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies needed for PyInstaller
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    gcc \
    libc6-dev \
    make \
 && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and source code
COPY pyproject.toml .
COPY uv.lock .
COPY sv_mcp/ ./sv_mcp

# Install your project and its dependencies
RUN pip install --no-cache-dir . \
    && pip install --no-cache-dir pyinstaller tomli pdm

RUN pdm install --prod --no-self

# Run build.py
WORKDIR /app/sv_mcp
RUN BINARY_NAME=sv-mcp-linux python build.py
# ----------------------------
# Stage 2: Final
# ----------------------------
FROM python:3.12-slim AS runtime

ENV MCP_DOCKER=true

WORKDIR /app

# Copy the statically named binary
COPY --from=builder /app/sv_mcp/dist/sv-mcp-linux /usr/local/bin/sv-mcp
RUN chmod +x /usr/local/bin/sv-mcp

# Run as non-root user
RUN groupadd -r sv-mcp && useradd -r -g sv-mcp sv-mcp
USER sv-mcp

ENTRYPOINT ["sv-mcp"]
CMD []
