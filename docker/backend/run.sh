#!/bin/bash

PORT=${PORT:-8000}
WORKERS=${WORKERS:-2}
gunicorn --pythonpath backend 'app:create_app()' -b 0.0.0.0:$PORT --workers $WORKERS