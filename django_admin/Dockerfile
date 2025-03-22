FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV HOME=/home/
ENV APP_HOME=/home/app
ENV PROJECT_DIR=/home/app/django_admin

RUN mkdir $APP_HOME
RUN mkdir $PROJECT_DIR
RUN mkdir $PROJECT_DIR/staticfiles/
RUN mkdir $PROJECT_DIR/exel/
RUN mkdir $PROJECT_DIR/mediafiles/
WORKDIR $PROJECT_DIR

COPY . $PROJECT_DIR
RUN ls -la $PROJECT_DIR

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN sed -i 's/\r$//g'  $PROJECT_DIR/entrypoint.sh
RUN chmod +x  $PROJECT_DIR/entrypoint.sh

ENTRYPOINT ["/home/app/django_admin/entrypoint.sh"]
