#!/bin/bash

if [[ $ENV = "local" ]]
then
    SCHEME="http"
    HOST="0.0.0.0:8000"
else
    SCHEME="https"
    HOST="api-limehome-task.azurewebsites.net"
fi

sed -i -e "s/ENV_API_KEY/${API_KEY}/g" /frontend/credentials.js
sed -i -e "s/ENV_HOST/${HOST}/g" /frontend/credentials.js
sed -i -e "s/ENV_SCHEME/${SCHEME}/g" /frontend/credentials.js

live-server --host=0.0.0.0 --port=${PORT} /frontend
