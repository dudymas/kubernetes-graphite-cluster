#!/bin/sh

set -x

cd /opt/graphite/webapp/ && python manage.py migrate --run-syncdb --noinput
mkdir -p /var/log/supervisor
exec /usr/local/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
