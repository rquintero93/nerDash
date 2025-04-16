FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir 'uv>=0.1.30'

# Create non-root user
RUN useradd --create-home appuser

# Switch to non-root user early
USER appuser
WORKDIR /app

# Set env for uv virtualenv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy and install deps
COPY --chown=appuser:appuser pyproject.toml ./
RUN uv sync --no-dev

# Copy app code
COPY --chown=appuser:appuser src src
COPY --chown=appuser:appuser .streamlit .streamlit

EXPOSE 8051

CMD ["streamlit", "run", "src/main.py", "--server.port=8051", "--server.address=0.0.0.0"]
