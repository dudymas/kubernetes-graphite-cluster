FROM	alpine:3.10.0

RUN apk add --update --no-cache py3-pip py3-twisted
RUN pip3 install supervisor whisper carbon kubernetes
RUN mkdir /kube-watch

ADD conf/carbon.conf.template /opt/graphite/conf/carbon.conf.template
ADD conf/storage-schemas.conf /opt/graphite/conf/storage-schemas.conf
ADD	./supervisord.conf /etc/supervisord.conf
ADD kube-watch.py /kube-watch/kube-watch.py
RUN mkdir -p /var/log/supervisor

EXPOSE 2003

CMD ["/usr/bin/supervisord"]
