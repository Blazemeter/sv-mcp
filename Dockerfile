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
COPY vs_mcp/ ./vs_mcp

# Install your project and its dependencies
RUN pip install --no-cache-dir . \
    && pip install --no-cache-dir pyinstaller tomli pdm

RUN pdm install --prod --no-self

# Run build.py
WORKDIR /app/vs_mcp
RUN python build.py
# ----------------------------
# Stage 2: Final
# ----------------------------
FROM python:3.12-slim AS runtime

ENV MCP_DOCKER=true

WORKDIR /app

# Copy the statically named binary
COPY --from=builder /app/vs_mcp/dist/bzm-mcp-linux /usr/local/bin/bzm-mcp
RUN chmod +x /usr/local/bin/bzm-mcp

# Run as non-root user
RUN groupadd -r bzm-mcp && useradd -r -g bzm-mcp bzm-mcp
USER bzm-mcp

ENTRYPOINT ["bzm-mcp"]
CMD []
