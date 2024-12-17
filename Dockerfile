# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Expose the port
EXPOSE 8000

# Command to run Gunicorn server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
