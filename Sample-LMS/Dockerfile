# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first to leverage caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 8001
EXPOSE 8001

# Set default port (Railway overrides this with its own PORT env var)
ENV PORT=8001

# Initialize the database with seed data and start the server
CMD ["sh", "-c", "python seed_test_users.py && uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
