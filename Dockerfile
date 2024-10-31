FROM python:3.10

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY . /code

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./apl_api /code/apl_api

CMD ["fastapi", "run", "apl_api/main.py", "--proxy-headers", "--port", "80"]
