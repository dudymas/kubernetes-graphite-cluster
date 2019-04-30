FROM	python:3-alpine

# Install required packages
RUN     apk add --update nodejs git build-base
RUN     pip install Twisted==13.2.0
RUN     pip install pytz
ARG graphite_version=1.1.x
RUN     git clone https://github.com/graphite-project/whisper.git /src/whisper            &&\
        cd /src/whisper                                                                   &&\
        git checkout $graphite_version                                                    &&\
        python setup.py install

RUN     git clone https://github.com/graphite-project/carbon.git /src/carbon              &&\
        cd /src/carbon                                                                    &&\
        git checkout $graphite_version                                                    &&\
        python setup.py install


ADD conf/carbon.conf.template /opt/graphite/conf/carbon.conf.template
ADD conf/storage-schemas.conf /opt/graphite/conf/storage-schemas.conf
ADD	./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN apk add npm && mkdir /kube-watch
RUN cd /kube-watch && npm install hashring kubernetes-client@5 json-stream
ADD kube-watch.js /kube-watch/kube-watch.js
RUN apk add supervisor
RUN mkdir -p /var/log/supervisor

EXPOSE 2003

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
