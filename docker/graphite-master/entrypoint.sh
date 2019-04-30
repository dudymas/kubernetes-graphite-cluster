#!/bin/sh

set -x

cd /opt/graphite/webapp/ && python manage.py migrate --run-syncdb --noinput
exec /usr/bin/supervisord
