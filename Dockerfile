# Dockerfile

FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set working directory
WORKDIR /app

# Copy dependency files first for cache efficiency
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --with dev

# Ensure config dir and copy Python startup script
RUN mkdir -p /root/.config/python
COPY .config/python/startup.py /root/.config/python/startup.py

# Set PYTHONSTARTUP for REPL sessions
ENV PYTHONSTARTUP=/root/.config/python/startup.py

# Set PYTHONSTARTUP env var for all interactive REPL sessions
ENV PYTHONSTARTUP=/root/.config/python/startup.py

# Now copy full project
COPY . .

# Default command
CMD ["poetry", "run", "pytest"]
