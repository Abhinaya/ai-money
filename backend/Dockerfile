# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock* /app/

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install

# Copy the rest of the application code to the container
COPY . /app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]