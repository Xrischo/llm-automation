FROM ollama/ollama
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip install ollama
COPY ./models /root/.ollama/models
COPY ./main.py /app
RUN mkdir -p /data/application
ENTRYPOINT ["python3", "/app/main.py"]
