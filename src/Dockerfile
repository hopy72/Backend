# our base image
FROM python:3.11

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# specify the port number the container should expose
EXPOSE 8080

# run the application
CMD ["python", "./main.py"]