FROM python:3.9

RUN pip install poetry

ADD ./pyproject.toml /worker/
ADD ./poetry.lock /worker/

WORKDIR /worker/

RUN poetry config virtualenvs.create false && poetry install --no-dev

ADD ./service /worker/service/

CMD ["python", "-m", "service"]
