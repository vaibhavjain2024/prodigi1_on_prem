FROM python:3.13-alpine

# Set the working directory
WORKDIR /app

# Install system dependencies required for psycopg2
# RUN apt-get update && apt-get install -y \
#     libpq-dev gcc && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Copy all .env files
COPY .env.* ./

# Define PYTHONPATH explicitly and add the shared directory
# ENV PYTHONPATH="/app:/app/modules"

# Pass the ENV variable
ENV ENV=dev

# Expose the port FastAPI will run on
EXPOSE 8001

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001","--workers", "4"]
