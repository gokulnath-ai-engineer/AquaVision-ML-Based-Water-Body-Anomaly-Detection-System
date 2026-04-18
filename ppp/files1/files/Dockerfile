# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for OpenCV, Rasterio, and PyTorch
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (Render/Railway use the PORT environment variable)
EXPOSE 8000

# Run the FastAPI server using Uvicorn (Render assigns dynamic ports)
CMD sh -c "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"
