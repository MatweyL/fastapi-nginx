FROM python:3.10

COPY . .

RUN mkdir storage && pip3 install -r requirements.txt

CMD  ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]