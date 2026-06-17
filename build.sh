#!/bin/bash
echo "Running collectstatic..."
python manage.py collectstatic --noinput
echo "Build complete!"
