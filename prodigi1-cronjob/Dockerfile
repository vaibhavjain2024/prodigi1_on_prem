# # Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory
WORKDIR /pc2

# Install cron
# RUN apt-get update && apt-get install -y cron

# Install Python dependencies (you may need to adjust based on your app's requirements)
COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir --timeout=120 -r requirements.txt

# Copy the rest of the application code
COPY . .

# Copy all .env files
COPY .env.* .

# Copy the crontab file (This will schedule your cron jobs)
# COPY crontab /etc/cron.d/cron-job

# Give execution rights to the cron job
# RUN chmod 0644 /etc/cron.d/cron-job

# Apply the cron job
# RUN crontab /etc/cron.d/cron-job

# Ensure the cron log file exists and cron runs with logs redirected to the file
# RUN touch /var/log/cron.log && chmod 0644 /var/log/cron.log

# Set environment variables (optional, can also be passed at runtime)
ENV ENV=local

# Expose the port for any other service you want to run inside the container (optional)
# EXPOSE 8007

# Start cron in the foreground and redirect cron logs to /var/log/cron.log
# CMD cron && tail -f /var/log/cron.log
# Run the FastAPI application using uvicorn
CMD ["python", "app/main.py"]