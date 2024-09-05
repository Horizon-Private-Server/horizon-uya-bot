FROM python:3.10-slim-buster as build-image

ARG FUNCTION_DIR=/code
RUN mkdir -p ${FUNCTION_DIR}
WORKDIR ${FUNCTION_DIR}

COPY requirements.txt .
RUN pip install -r thug_requirements.txt
ENV USE_ENV_VARS Yes

# Copy function code
COPY . ${FUNCTION_DIR}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD python thug.py
