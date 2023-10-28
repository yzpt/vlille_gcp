# Use an official Python runtime as a parent image
FROM python:3.10-slim

WORKDIR /app

COPY . /app


# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run your script when the container launches
CMD ["python3", "app.py"]
