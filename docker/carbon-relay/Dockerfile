FROM	alpine:3.10.0

RUN apk add --update --no-cache py3-pip py3-twisted npm
RUN pip3 install supervisor whisper carbon
RUN mkdir /kube-watch
RUN cd /kube-watch && npm install hashring kubernetes-client@5 json-stream

ADD conf/carbon.conf.template /opt/graphite/conf/carbon.conf.template
ADD conf/storage-schemas.conf /opt/graphite/conf/storage-schemas.conf
ADD	./supervisord.conf /etc/supervisord.conf
ADD kube-watch.js /kube-watch/kube-watch.js
RUN mkdir -p /var/log/supervisor

EXPOSE 2003

CMD ["/usr/bin/supervisord"]
