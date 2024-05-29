# Application monitoring with graphite and grafana

## Task 1

Write a simple application that sometimes (once every 30 calls) processes the request slower.
Monitor number of requests and processing time.
Create dashboard in grafana that will present: 
- mean, 90-percentile and max of processing time
- number of requests

## Run grafana with graphite in docker

### Common docker network bridge

For MacOS we need to create dedicated network to enable communication between containers.
```bash
docker network create graphite-net
```

### Run grafana

```bash
docker pull grafana/grafana-oss

docker run -d --network=graphite-net -p 3000:3000 --name grafana grafana/grafana-oss
```

(add sudo if user is not in docker group)

### Run graphite

```bash
docker pull  graphiteapp/graphite-statsd

docker run -d \
 --name graphite \
 --restart=always \
 --network=graphite-net \
 -p 8125:8125/udp -p 80:80 \
 graphiteapp/graphite-statsd
```

Log into grafana:
http://127.0.0.1:3000/

Add datasource with type: graphite and ip address: http://graphite

### Check

Send simple single metric:

```bash
echo -n "test:20|c" | nc -w 1 -u 127.0.0.1 8125;
```

verify on graphite web:
http://localhost/render?from=-10mins&until=now&target=stats.test

verify on grafana:

Explore > Series: stats+test

## Task 2

- Add /health endpoint to app
- Create LB (similar to lab10) which checks created endpoint
- Deploy two apps
- Deploy LB
- Check if traffic is distributed
- Turn off one of app
- Verify if /health returns unhealthy state - LB will not forward traffic
- Check on grafana if you can observe:
  - number of processed request by app and globally

### Example

Build app docker and run two app instances.
Please note, that this example is configured for user-defined bridge docker networking. 
If other type of networking was chosen - some amendments in configuration must be made.

In app directory:

```bash
docker build -t app .

docker run -d --rm -p 8001:8000 --network=graphite-net -e "APP_NAME=app1" --name app1 app
docker run -d --rm -p 8002:8000 --network=graphite-net -e "APP_NAME=app2" --name app2 app
```

Run load balancer (order is important)
in lb directory:

```bash
docker build -t lb .
docker run -d --rm -p 8000:8000 -p 10000:10000 --network=graphite-net  --name lb lb
```

#### Verify
Check access to single apps:
- App1: http://127.0.0.1:8001/?cnt=2
- App2: http://127.0.0.1:8002/?cnt=2
- By LB: http://127.0.0.1:8000/?cnt=2

Check status in LB.
Now you can experiment with turning off application by API:
http://127.0.0.1:8001/docs -> send request to /turnoff
Is it visible for LB ?

Check result on grafana:
- create dashboard that compare App1 vs App2
- create dashboard that aggregate data from both apps