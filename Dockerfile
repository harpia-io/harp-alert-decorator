FROM python:3.10.9

WORKDIR /code
COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get -y install librdkafka-dev
RUN pip install -r requirements.txt
RUN pip install "uvicorn[standard]" gunicorn==20.1.0
COPY . .
RUN python setup.py install

CMD ["gunicorn", "harp_alert_decorator.__main__:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8081", "--workers", "1", "--threads", "1", "--timeout", "120"]