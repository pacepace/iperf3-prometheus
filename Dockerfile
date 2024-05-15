# syntax=docker/dockerfile:1
#
# This Dockerfile is used to build the docker image for Discodon.
#

# install depencencies and compile (this is a multi-stage build)
#
# python multi-stage build info: https://pythonspeed.com/articles/multi-stage-docker-python/
#
# the image used in this stage must include the compiler and build tools
#
# Docker Scount recommended python:alpine, but this doesn't work.
FROM python:3.10 AS compile-image
# make for easier cleanup
LABEL stage=builder

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# store the virtual environment in the project directory
ENV PIPENV_VENV_IN_PROJECT=1

# image should be updated already
# RUN apt-get update \
# && DEBIAN_FRONTEND=noninteractive \
#   apt-get upgrade -yy
#
WORKDIR /opt/venv

ENV PATH="/opt/venv/.venv/bin:$PATH"

# !!! voodoo !!!
# !!! don't get ls RUNs below
# !!! voodoo !!!
RUN pip install pipenv
COPY Pipfile Pipfile.lock /opt/venv/
RUN ls -la
RUN pipenv install
RUN ls -la
COPY . .
RUN ls -la

# build the runtime image
#
# python:3 may cause problems on azure (3.11 is the apparent issue)
# using -slim builds will reduce the number of vulnerabilities
# use -slim builds for production and non-slim for development
FROM python:3.10-slim as runtime-image

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# store the virtual environment in the project directory
ENV PIPENV_VENV_IN_PROJECT=1

# install iperf3
RUN apt-get update \
&& DEBIAN_FRONTEND=noninteractive \
apt-get install -yy iperf3

# Creates a non-root user with an explicit UID
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser
USER appuser

# copy compiled files into the runtime image
COPY --from=compile-image --chown=appuser:appuser /opt/venv /opt/venv

# dependencies installed in compile-image

# set the working directory
WORKDIR /opt/venv

# use the virtual environment
ENV PATH="/opt/venv/.venv/bin:$PATH"
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "iperf3-prometheus.py"]
EXPOSE 9200
