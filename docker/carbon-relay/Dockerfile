FROM	alpine:3.10.0

RUN apk add --update --no-cache py3-pip py3-twisted python3-dev libffi-dev build-base \
  && CASS_DRIVER_BUILD_CONCURRENCY=8 pip3 install biggraphite \
  && pip3 install supervisor whisper carbon kubernetes \
  && apk del build-base python3-dev libffi-dev \
  && apk add py3-cairo
RUN mkdir /kube-watch

ADD conf/carbon.conf.template /opt/graphite/conf/carbon.conf.template
ADD conf/storage-schemas.conf /opt/graphite/conf/storage-schemas.conf
ADD	./supervisord.conf /etc/supervisord.conf
ADD kube-watch.py /kube-watch/kube-watch.py
RUN mkdir -p /var/log/supervisor

EXPOSE 2003

CMD ["/usr/bin/supervisord"]
