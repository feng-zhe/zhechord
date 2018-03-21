FROM ubuntu:16.04
LABEL maintainer "zhef@umich.edu"
ENV LC_ALL="C.UTF-8" LANG="C.UTF-8"
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        libssl-dev \
        libffi-dev \
        python-dev \
        python3 \
        python3-pip \
        git
COPY ./ /root/project/
WORKDIR /root/project/
RUN pip3 install pipenv && \
    pipenv install
# use entrypoint so that we can pass arguements when starting containers
ENTRYPOINT ["pipenv","run", "python", "server/mychord/server.py"]
