# Base image with Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install curl for healthcheck and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# # Environment variables
# ENV MONGO_URI=mongodb+srv://minh:minhminh@cluster0.fm3vl.mongodb.net/Anhminh

# Copy application code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]