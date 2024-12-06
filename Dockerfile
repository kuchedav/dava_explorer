FROM python:3.8

RUN mkdir /app
WORKDIR /app/

COPY src/dava_explorer/. .

ENTRYPOINT ["tail", "-f", "/dev/null"]
