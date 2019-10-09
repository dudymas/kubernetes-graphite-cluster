#!/bin/sh

set -x

mkdir -p /opt/graphite/storage/log/webapp
touch /opt/graphite/storage/log/webapp/info.log
chmod 0775 -R /opt/graphite/storage/log/webapp

cd /opt/graphite/webapp/ && ./manage migrate --run-syncdb --noinput
mkdir -p /var/log/supervisor
exec /usr/bin/supervisord -c /etc/supervisord.conf
