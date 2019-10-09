#!/bin/sh

set -x

if [ -n "$CURATOR_RETENTION" ]
then
  sed -i "s/{{CURATOR_RETENTION}}/$CURATOR_RETENTION/g" /etc/cron.d/curator.sh
  crontab -u root /etc/cron.d/curator.cron
fi

mkdir -p /var/log/supervisor

exec /usr/bin/supervisord -c /etc/supervisord.conf
