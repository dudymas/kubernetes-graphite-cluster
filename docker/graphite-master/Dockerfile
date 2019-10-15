FROM	alpine:3.10.0

RUN apk add --update --no-cache py3-pip py3-cairo py3-cffi py3-twisted nginx
RUN pip3 install supervisor graphite-web whisper carbon redis-py-cluster gunicorn
RUN mkdir /kube-watch

# Add env vars
ENV PYTHONPATH=/opt/graphite/webapp
ENV DJANGO_SETTINGS_MODULE=graphite.settings

# Add system service config
ADD	./nginx/nginx.conf /etc/nginx/nginx.conf
ADD	./supervisord.conf /etc/supervisord.conf

# Add graphite config
ADD	./webapp/initial_data.json /opt/graphite/webapp/graphite/initial_data.json
ADD	./webapp/local_settings.py.template /opt/graphite/webapp/graphite/local_settings.py.template
ADD	./webapp/tags/rediscluster.py /opt/graphite/webapp/graphite/tags/rediscluster.py
ADD	./conf/carbon.conf /opt/graphite/conf/carbon.conf
ADD	./conf/storage-schemas.conf /opt/graphite/conf/storage-schemas.conf
ADD	./conf/storage-aggregation.conf /opt/graphite/conf/storage-aggregation.conf
RUN	mkdir -p /opt/graphite/storage/whisper /opt/graphite/storage/log/webapp /run/nginx
RUN	touch /opt/graphite/storage/graphite.db /opt/graphite/storage/index /opt/graphite/storage/log/webapp/info.log
RUN	chmod 0775 -R /opt/graphite/storage
RUN	chmod 0664 /opt/graphite/storage/graphite.db
ADD ./webapp/manage /opt/graphite/webapp
ADD kube-watch.py /kube-watch/kube-watch.py

ADD entrypoint.sh /entrypoint.sh
# Nginx
EXPOSE	80
# Carbon line receiver port
# expose	2003
# Carbon UDP receiver port
# expose	2003/udp
# Carbon pickle receiver port
# expose	2004
# Carbon cache query port
# expose	7002

CMD	["/entrypoint.sh"]
