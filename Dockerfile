# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure static directories exist
RUN mkdir -p static/animations data/fallback_logs

# Expose the port the app runs on
EXPOSE 8080

# Define environment variable for SDL to run headlessly
ENV SDL_VIDEODRIVER=dummy
ENV PORT=8080

# Run the application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
