# Load balancing lab

## 1. Create a Git repository

Create an empty Git repository using one of the free providers:
Github/Gitlab/etc. Repository can be public or private, but later you will want
to check out the repository on the provided servers, so if it is private, you
will need to configure authorization on each of the servers.

You can use some of the work done today for your final project.

## 2. Initialize an HTTP app in the Git repository, using language and framework of choice

Use any application framework you like. You should end up with some Python/Java
etc. files and a Dockerfile that will:

    - Install the compiler for you app (if relevant, e.g JDK)
    - Compile your app (if relevant)
    - Install runtime for your app (e.g. Python)
    - Run the app (e.g. execute python app.py)

Starting the Docker container built from the image should start an HTTP server
at some port.

### Example with Python and FastAPI

1. In the root directory of the Git repository create an `app_server` directory.

2. In the `app_server/` directory create a `src/` directory for
   the source code of your app. Create a `src/main.py` file:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

3. In the `app_server/` directory create a `requirements.txt` file:

```
fastapi
uvicorn[standard]
```

4. In the `app_server/` directory create a `Dockerfile`:

```dockerfile
FROM debian:bullseye-slim

RUN apt-get update && \
	apt-get install -y --no-install-recommends python3 python3-pip

COPY ["requirements.txt", "/tmp/requirements.txt"]

RUN ["pip3", "install", "-r", "/tmp/requirements.txt"]

COPY ["src/", "/opt/app_server"]

WORKDIR "/opt/app_server"

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "main:app"]
```

5. Build and run the dockerfile:

```bash
sudo docker build . -t app_server
sudo docker run --network=host app_server

```

6. You should be able to send a request to the app server now:

```
> curl localhost:8000
{"message":"Hello World"}
```

7. Commit your changes to the repo

8. Checkout the repo on at least two servers, run the app

9. In the root directory of the Git repository create an `app_lb` directory.

10. Create a `Dockerfile`:

```dockerfile
FROM haproxy:2.5
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
```

11. Create a `haproxy.cfg`:

```
defaults
        mode http

        option httplog
        log stdout format raw local0 info

        timeout client 60000
        timeout connect 1000
        timeout server 10000

frontend http
        bind 0.0.0.0:9000

        default_backend app_server

backend app_server
        balance roundrobin
        server stXYZvmANC_rtb_lab_pl stXYZvmANC.rtb-lab.pl:8000
        # ...


frontend stats
        bind 0.0.0.0:10000
        stats enable
        stats uri /
        stats refresh 5s
```

12. Commit the changes, checkout the repo on another server

13. Build the image in the `app_lb` directory and run the load balancer:

```
sudo docker build -t my-proxy .
sudo docker run --network=host --privileged my-proxy

```

14. Check that the LB is working:

```
curl stXYZvmANC.rtb-lab.pl:9000

```

15. Check that the LB stats page is working by opening `stXYZvmANC.rtb-lab.pl:10000` in the browser
