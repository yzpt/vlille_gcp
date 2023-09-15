# Use an official Python runtime as a parent image
FROM python:3.10-slim

WORKDIR /app
COPY . /app

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0


# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8080

# Run your script when the container launches
CMD ["python", "app.py"]
