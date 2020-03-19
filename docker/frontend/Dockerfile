FROM node:10

ENV PORT 8001

COPY ./frontend/package*.json ./

RUN npm install -g
RUN npm install -g live-server@1.2.1

# Bundle app source
COPY ./docker/frontend/run.sh /run.sh
RUN chmod +x /run.sh
COPY ./frontend /frontend

WORKDIR /frontend

EXPOSE ${PORT}
ENTRYPOINT ["/run.sh"]
