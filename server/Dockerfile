FROM python:3.12-slim

WORKDIR /code

COPY poetry.lock pyproject.toml ./

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --without dev,test \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
