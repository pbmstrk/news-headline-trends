FROM python:3.11-slim

WORKDIR /nyt-data

COPY ./requirements.txt /nyt-data/

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY main.py /nyt-data/api/main.py

EXPOSE 8050

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8050"]
