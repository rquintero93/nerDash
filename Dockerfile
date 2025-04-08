# Start from the official Python 3.12 base image
FROM python:3.11-slim-bookworm

# apt update and install build-essential for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install pipx and use it to install uv
RUN pip install --no-cache-dir pipx && \
    pipx install uv

# Ensure pipx-installed binaries (like uv) are available on PATH
ENV PATH="/root/.local/bin:$PATH"

# Set working directory for the application
WORKDIR /app

# Copy dependency specification files
COPY pyproject.toml ./

# Install project dependencies
RUN uv sync --no-dev

# Create a non-root user for running the application
RUN useradd --create-home appuser
# Copy the rest of the application code into the container
COPY src src
COPY .streamlit .streamlit

RUN chown -R appuser:appuser /app
USER appuser

# If uv created a virtual environment (.venv), activate it for runtime
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Expose the port for streamlit
EXPOSE 8051

#default command to run the application
CMD ["streamlit", "run", "src/main.py", "--server.port=8051", "--server.address=0.0.0.0"]
