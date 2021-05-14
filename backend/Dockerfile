FROM ubuntu:18.04

LABEL dock.img.name="my.project.com/dq-glue-deequ/1.0.0"  \
      dock.schema-version="0.1" \
      dock.img.description="Docker image for deploying deequ based Data Quality framework" \
      dock.docker.run="docker run -it"

RUN echo "APT::Acquire::Retries \"5\";" > /etc/apt/apt.conf.d/80-retries

RUN apt-get update && apt-get install -y software-properties-common wget
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.7 python3.7-dev python3-venv python-dateutil

RUN wget -q https://bootstrap.pypa.io/get-pip.py && python3.7 get-pip.py

COPY requirements.txt .
RUN pip install --upgrade pip \
	&& pip install --no-deps -r requirements.txt

RUN mkdir ~/.npm-global
ENV PATH=~/.npm-global/bin:$PATH
ENV NPM_CONFIG_PREFIX=~/.npm-global
RUN npm install -g serverless serverless-pseudo-parameters serverless-python-requirements serverless-wsgi --unsafe
