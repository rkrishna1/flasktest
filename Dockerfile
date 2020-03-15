FROM python:3.7.6
RUN apt-get update && apt-get upgrade
RUN pip install flask flask_migrate flask_sqlalchemy SQLAlchemy flask_cors
RUN apt install -y python2.7
RUN apt-get -y install sqlite3 libsqlite3-dev ffmpeg
RUN mkdir -p ~/task ~/task/content
COPY app /task/app
COPY bin /task/bin
COPY utils /task/utils
COPY server.py /task/server.py
RUN rm -rf app/app.db
WORKDIR /task
RUN flask db init
EXPOSE 5000
RUN export FLASK_APP=server.py
RUN export FLASK_ENV=development
CMD ["flask", "run", "--host=0.0.0.0"]