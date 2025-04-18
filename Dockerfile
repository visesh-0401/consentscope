# Base image
FROM python:3.12-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Chrome & ChromeDriver dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set up work directory
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
