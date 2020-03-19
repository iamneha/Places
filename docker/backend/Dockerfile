FROM python:3.7-slim-stretch

ENV PORT 8000
ENV WORKERS 4

COPY ./requirements.txt /backend/requirements.txt
RUN pip install -U pip && pip install -r /backend/requirements.txt

COPY docker/backend/run.sh /run.sh
RUN chmod +x /run.sh

COPY . /backend

WORKDIR /backend

EXPOSE ${PORT}
ENTRYPOINT ["/run.sh"]
