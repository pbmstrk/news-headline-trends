FROM python:3.11-slim

WORKDIR /nytdata 

COPY . ./app/

RUN pip install --upgrade pip
RUN pip install -r app/requirements.txt 

EXPOSE 8050

CMD ["gunicorn", "-b", "0.0.0.0:8050", "--reload", "app.app:server"]