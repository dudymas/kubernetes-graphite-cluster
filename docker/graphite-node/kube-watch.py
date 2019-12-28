import os, subprocess

from kubernetes import client, config, watch


DEFAULT_SERVICE=os.getenv('REDIS_SERVICE', 'redis-tags.stats.svc')
config_template_path = '/opt/graphite/webapp/graphite/local_settings.py.template'
config_file_path = '/opt/graphite/webapp/graphite/local_settings.py'
target_program = 'graphite-webapp'
target_service = 'redis-tags'
template_field = '@@REDIS_CLUSTER@@'


with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as nsf:
    namespace = nsf.read()


def get_cluster_ip(services):
    if not services or services.spec.cluster_ip in {None, 'None'}:
        return DEFAULT_SERVICE
    return services.spec.cluster_ip


def update_config(redis_ip, template_field):
    if len(redis_ip.strip()) == 0:
        return
    with open(config_template_path) as cf:
        configText = cf.read()
    configText = configText.replace(template_field, redis_ip.strip())
    with open(config_file_path, 'w') as cf:
        cf.write(configText)
    subprocess.run(f'supervisorctl restart {target_program}', shell=True, check=True)


def watch_service(target_service, template_field):
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()
    events = w.stream(v1.list_namespaced_service,
        namespace,
        field_selector=f'metadata.name={target_service}')
    for event in events:
        if 'object' in event:
            ip = get_cluster_ip(event.get('object'))
            update_config(ip, template_field)


def main():
    watch_service(target_service, template_field)


if __name__ == "__main__":
    main()
