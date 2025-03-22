FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV HOME=/home/
ENV APP_HOME=/home/app
ENV PROJECT_DIR=/home/app/telegram_bot

RUN mkdir $APP_HOME
RUN mkdir $PROJECT_DIR
RUN mkdir $PROJECT_DIR/loggs/

WORKDIR $PROJECT_DIR

COPY . $PROJECT_DIR
RUN ls -la $PROJECT_DIR

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN sed -i 's/\r$//g'  $PROJECT_DIR/entrypoint.sh
RUN chmod +x  $PROJECT_DIR/entrypoint.sh

ENTRYPOINT ["/home/app/telegram_bot/entrypoint.sh"]
