FROM nginx/unit:1.28.0-python3.10
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


WORKDIR /webapp
COPY ./requirements.txt /webapp/
RUN apt update && apt install -y python3-pip                                  \
    && pip3 install -r requirements.txt                                       \
    && apt remove -y python3-pip                                              \
    && apt autoremove --purge -y                                              \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list
COPY unit_config.json /docker-entrypoint.d/
COPY mysite /webapp/src
WORKDIR /webapp/src
RUN  SECRET_KEY=empoty  python manage.py collectstatic --noinput
EXPOSE 80
VOLUME ["/media"]
