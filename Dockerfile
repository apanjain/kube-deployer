# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.7-slim

# environment variables
ENV APP_HOME=/app \
    PYTHONUNBUFFERED=1 \
    HELLOWORLD_IMAGE_LOCATION=$HELLOWORLD_IMAGE_LOCATION \
    UPDATED_IMAGE_LOCATION=$UPDATED_IMAGE_LOCATION

WORKDIR $APP_HOME

# Install production dependencies.
RUN pip install Flask gunicorn kubernetes pytz

# Copy local code to the container image.
COPY . ./

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app