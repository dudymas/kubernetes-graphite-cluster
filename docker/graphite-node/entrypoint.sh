#!/bin/sh

set -x

if [ -n "$CURATOR_RETENTION" ]
then
  sed -i "s/{{CURATOR_RETENTION}}/$CURATOR_RETENTION/g" /etc/cron.d/curator.sh
  crontab -u root /etc/cron.d/curator.cron
fi

mkdir -p /var/log/supervisor
mkdir -p /opt/graphite/storage/log/webapp
touch /opt/graphite/storage/log/webapp/info.log
chmod 0775 -R /opt/graphite/storage/log/webapp

exec /usr/bin/supervisord -c /etc/supervisord.conf
