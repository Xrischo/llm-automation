FROM ubuntu:22.04
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir -p /data/application

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -U stable-ts

COPY ./voices /app/tts/

COPY ./piper_linux_x86_64.tar.gz /app/tts/
RUN tar -xzf /app/tts/piper_linux_x86_64.tar.gz -C /app/tts/

COPY ./main.py /app

ENTRYPOINT ["/bin/sh", "-c", "tail -f /dev/null"]
