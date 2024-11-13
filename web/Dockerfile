# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install Flask and psycopg2 for PostgreSQL
RUN pip install flask psycopg2

# Set the default command to run the app
CMD ["python", "app.py"]
