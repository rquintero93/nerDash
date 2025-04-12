FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Use pip to install uv directly instead of pipx
RUN pip install --no-cache-dir 'uv>=0.1.30'

# Set environment for uv virtualenv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --no-dev

# Add application code
COPY src src
COPY .streamlit .streamlit

# Add non-root user & set permissions
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8051

CMD ["streamlit", "run", "src/main.py", "--server.port=8051", "--server.address=0.0.0.0"]
