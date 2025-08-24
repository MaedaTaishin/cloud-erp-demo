# Use a slim version of the official Python image as a base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
# This is a best practice to leverage Docker's layer caching
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application code into the container
COPY . .

# Expose the port that the Flask app will run on
EXPOSE 5000

# Set the FLASK_APP environment variable
ENV FLASK_APP=app:app

# The command to run the application when the container starts
# We use 'flask run' in development.
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]