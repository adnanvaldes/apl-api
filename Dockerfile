
FROM python:3.9


WORKDIR /code


COPY ./requirements.txt /code/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./apl_api /code/apl_api


CMD ["fastapi", "run", "apl_api/main.py", "--proxy-headers", "--port", "80"]