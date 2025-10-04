# 1. Specify the base image
# Use a lightweight Python 3.9 image for a smaller final image size.
FROM python:3.9-slim

# 2. Set the working directory inside the container
# All subsequent commands will be executed relative to this directory.
WORKDIR /app

# 3. Handle Dependencies
# Copy the requirements file and install dependencies first to leverage Docker layer caching.
COPY requirements.txt .
RUN pip install -r requirements.txt

# 4. Copy Application Files
# Copy the rest of the application code (e.g., server.py, client.py) into the container.
COPY . /app

# 5. Expose the port the application is listening on
# This is documentation, telling users that the service runs on port 8080.
EXPOSE 8080

# 6. Define the command to run when the container starts
# This launches your Python server application.
CMD ["python", "server.py"]