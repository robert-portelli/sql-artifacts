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
# the container is the env
ENV POETRY_VIRTUALENVS_CREATE=false
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set working directory
WORKDIR /app

# Copy dependency files first for cache efficiency
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --with dev

# Now copy the full project
COPY . .

CMD ["poetry", "run", "pytest"]
