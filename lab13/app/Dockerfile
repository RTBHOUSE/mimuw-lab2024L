FROM debian:bullseye-slim

RUN apt-get update && \
	apt-get install -y --no-install-recommends python3 python3-pip


RUN python3 -m pip install fastapi uvicorn statsd

COPY ["src/", "/opt/app_server"]

WORKDIR "/opt/app_server"

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "main:app"]