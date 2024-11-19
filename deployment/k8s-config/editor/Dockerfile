FROM ubuntu:22.04
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir -p /data/application

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./test/ /main/test

ENTRYPOINT ["/bin/sh", "-c", "tail -f /dev/null"]
