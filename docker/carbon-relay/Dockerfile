from	python:3-alpine

# Install required packages
run apk add --update nodejs git build-base
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


add conf/carbon.conf.template /opt/graphite/conf/carbon.conf.template
add conf/storage-schemas.conf /opt/graphite/conf/storage-schemas.conf
add	./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir /kube-watch
RUN cd /kube-watch && npm install hashring kubernetes-client@5 json-stream
add kube-watch.js /kube-watch/kube-watch.js

EXPOSE 2003

CMD ["/usr/bin/supervisord"]
