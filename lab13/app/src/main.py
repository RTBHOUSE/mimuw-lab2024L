import os
import random
import time

from fastapi import FastAPI, Response, status
from statsd.defaults.env import StatsClient

app = FastAPI()

statsd = StatsClient('graphite', 8125, prefix=os.environ.get("APP_NAME", "app"))

app_status = {"status": "healthy"}


def calc(cnt: int = None):
    r = 1
    for i in range(1, cnt):
        r *= i
    return r


@app.post("/turnoff")
def turnoff():
    app_status["status"] = "unhealthy"
    app_status["details"] = "turned off"


@app.head("/health")
def healthcheck(response: Response):
    if app_status.get("status", "") != "healthy":
        response.status_code = status.HTTP_418_IM_A_TEAPOT
    else:
        response.status_code = status.HTTP_200_OK


@app.get("/")
@statsd.timer("root")
def root(cnt: int = None):
    statsd.incr("root.called")
    if cnt:
        sleep_time = random.randint(0, cnt * 3)
        time.sleep(sleep_time / 5)
        statsd.gauge("root.cnt", cnt)
        statsd.gauge("root.sleep_time", sleep_time)
        statsd.incr("root.with_cnt")
        with statsd.timer('root.calc'):
            return {"message": f'{calc(cnt)}'}
    return {"message": "No value provided!"}
