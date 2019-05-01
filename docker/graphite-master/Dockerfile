FROM	python:3-alpine

# Install required packages
RUN     apk add --update --no-cache git build-base py-cairo-dev libffi-dev npm nginx
RUN     pip3 install Twisted pytz supervisor gunicorn
ARG graphite_version=1.1.x
RUN     git clone https://github.com/graphite-project/whisper.git /src/whisper            &&\
        cd /src/whisper                                                                   &&\
        git checkout $graphite_version                                                    &&\
        python setup.py install

RUN     git clone https://github.com/graphite-project/carbon.git /src/carbon              &&\
        cd /src/carbon                                                                    &&\
        git checkout $graphite_version                                                    &&\
        python setup.py install


RUN     git clone https://github.com/graphite-project/graphite-web.git /src/graphite-web  &&\
        cd /src/graphite-web                                                              &&\
        git checkout $graphite_version                                                    &&\
        python setup.py install                                                           &&\
        pip install -r requirements.txt                                                   &&\
        python check-dependencies.py

# fixes fatal error "Your WhiteNoise configuration is incompatible with WhiteNoise v4.0"
RUN     /usr/bin/yes | pip uninstall whitenoise                                           &&\
        pip install "whitenoise<4"

# Add system service config
ADD	./nginx/nginx.conf /etc/nginx/nginx.conf
ADD	./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Add graphite config
ADD	./webapp/initial_data.json /opt/graphite/webapp/graphite/initial_data.json
ADD	./webapp/local_settings.py.template /opt/graphite/webapp/graphite/local_settings.py.template
ADD	./conf/carbon.conf /opt/graphite/conf/carbon.conf
ADD	./conf/storage-schemas.conf /opt/graphite/conf/storage-schemas.conf
ADD	./conf/storage-aggregation.conf /opt/graphite/conf/storage-aggregation.conf
RUN	mkdir -p /opt/graphite/storage/whisper
RUN	touch /opt/graphite/storage/graphite.db /opt/graphite/storage/index
RUN	chmod 0775 /opt/graphite/storage /opt/graphite/storage/whisper
RUN	chmod 0664 /opt/graphite/storage/graphite.db
RUN cp /src/graphite-web/webapp/manage.py /opt/graphite/webapp

RUN mkdir /kube-watch
RUN cd /kube-watch && npm install hashring kubernetes-client@5 json-stream
ADD kube-watch.js /kube-watch/kube-watch.js

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
