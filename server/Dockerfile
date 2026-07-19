# Use an official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the application port
EXPOSE 5000

# Start the server
CMD ["python", "app.py"]