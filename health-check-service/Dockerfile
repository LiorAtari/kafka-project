FROM python:3.11

COPY . /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENTRYPOINT [ "python", "health_check_service.py" ]