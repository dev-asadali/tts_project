# Use the official Python image as a base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=2000  -r requirements.txt

# Copy the Django project into the container
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port Django runs on
EXPOSE 5000

# Start the Django development server
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && python manage.py runserver 0.0.0.0:5000"]
