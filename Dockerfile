FROM python:3.9-alpine3.13

COPY pytype.py /app/app.py
COPY requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt

CMD ["python3", "/app/app.py"]