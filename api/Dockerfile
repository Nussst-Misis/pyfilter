FROM python:3.9

RUN pip install poetry

ADD ./pyproject.toml /server/
ADD ./poetry.lock /server/

WORKDIR /server/

RUN poetry config virtualenvs.create false && poetry install --no-dev

ADD ./app /server/app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
