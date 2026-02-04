# syntax=docker/dockerfile:1
FROM python:3.14.2-slim

WORKDIR /app

COPY main.py .
COPY forms.py .
COPY inventree_calls.py .
COPY static .
ADD static static
COPY templates .
ADD templates templates
COPY config.py .

COPY requirements.txt .

RUN pip install -r requirements.txt
EXPOSE 8080
CMD [ "python3" , "main.py"]

