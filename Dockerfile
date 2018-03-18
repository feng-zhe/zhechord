FROM ubuntu:16.04
LABEL maintainer "zhef@umich.edu"
RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        git && \
    pip3 install pipenv
ENV LC_ALL="C.UTF-8" LANG="C.UTF-8"
COPY ./ /root/project/
WORKDIR /root/project/server/mychord/
RUN pipenv install
# use entrypoint so that we can pass arguements when starting containers
ENTRYPOINT ["pipenv","run", "python", "server.py"]
