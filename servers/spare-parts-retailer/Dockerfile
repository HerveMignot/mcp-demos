# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the project root into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents (server.py, catalog.py, etc.) into the container at /app
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the fastmcp server
CMD ["fastmcp", "run", "server.py", "--transport", "http", "--port", "8000", "--host", "0.0.0.0"]
