FROM python:3.10-alpine

WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY main.py /code/

EXPOSE 5000

ENV FLASK_APP main

# not a production grade app
CMD flask run
