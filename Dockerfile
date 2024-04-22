# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install Gunicorn and other needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 5003 available to the world outside this container
EXPOSE 5003

# Define environment variable to store the location of Gunicorn configuration
ENV GUNICORN_CONF="gunicorn.conf.py"
ENV APP_MODULE="app:app"

# Run Gunicorn with specified configuration and app module
CMD ["gunicorn", "--config", "$GUNICORN_CONF", "$APP_MODULE"]
#CMD gunicorn --config $GUNICORN_CONF $APP_MODULE
CMD ["gunicorn", "--certfile", "/etc/letsencrypt/live/vauva.ampiainen.net/fullchain.pem", "--keyfile", "/etc/letsencrypt/live/vauva.ampiainen.net/privkey.pem", "--ssl-version", "5", "--cert-reqs", "0", "--bind", "0.0.0.0:5003", "app:app"]

