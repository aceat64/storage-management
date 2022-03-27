# Based off: https://github.com/bmaingret/coach-planner

ARG APP_NAME=storage_management
ARG APP_PATH=/opt/${APP_NAME}
ARG PYTHON_VERSION=3.10-alpine
ARG POETRY_VERSION=1.1.12


#
# Stage: prep
# Load the source files and relevant system dependencies
#
FROM python:${PYTHON_VERSION} as prep
ARG APP_NAME
ARG APP_PATH
ARG POETRY_VERSION

ENV \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 
ENV \
  POETRY_VERSION=$POETRY_VERSION \
  POETRY_HOME="/opt/poetry" \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1

# Install build deps
RUN apk --no-cache add curl gcc musl-dev libressl-dev libffi-dev python3-dev postgresql-dev

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Import our project files
WORKDIR $APP_PATH
COPY ./poetry.lock ./pyproject.toml ./manage.py ./
COPY ./$APP_NAME ./$APP_NAME


#
# Stage: develop
#
FROM prep as develop

# Install dependencies
WORKDIR $APP_PATH
RUN poetry install

ENTRYPOINT ["poetry", "run"]
CMD ["python", "manage.py", "runserver"]


#
# Stage: build
#
FROM prep as build
ARG APP_PATH

WORKDIR $APP_PATH
RUN poetry build --format wheel
RUN poetry export --format requirements.txt --output constraints.txt --without-hashes


#
# Stage: production
#
FROM python:$PYTHON_VERSION as production
ARG APP_NAME
ARG APP_PATH

ENV \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1

ENV \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

# Get build artifact wheel and install it respecting dependency versions
WORKDIR $APP_PATH
COPY --from=build $APP_PATH/dist/*.whl ./
COPY --from=build $APP_PATH/constraints.txt ./
RUN apk --no-cache add libpq
# Done as one command so we don't increase the size of the final image with the dev packages
RUN apk --no-cache add gcc musl-dev postgresql-dev && \
  pip install ./$APP_NAME*.whl --constraint constraints.txt && \
  apk del gcc musl-dev postgresql-dev

# gunicorn port. Naming is consistent with GCP Cloud Run
ENV PORT=8888
# export APP_NAME as environment variable for the CMD
ENV APP_NAME=$APP_NAME

# Entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind :$PORT", "--workers 1", "--threads 1", "--timeout 0", "${APP_NAME}.wsgi:application"]