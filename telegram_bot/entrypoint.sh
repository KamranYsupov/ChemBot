#!/bin/sh
sleep 5

python update_models.py
python main.py

exec "$@"
