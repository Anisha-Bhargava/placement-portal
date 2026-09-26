# Use a lightweight Python base image
FROM python:3.13-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency file first (for better caching)
COPY requirement.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirement.txt

# Copy the rest of the app code
COPY . .

# Flask runs on port 5000 by default
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]