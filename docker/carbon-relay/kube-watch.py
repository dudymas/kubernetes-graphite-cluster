import subprocess

from kubernetes import client, config, watch


confid_template_path = '/opt/graphite/webapp/graphite/local_settings.py.template'
config_file_path = '/opt/graphite/webapp/graphite/local_settings.py'
target_program = 'graphite-webapp'
target_service = 'redis-tags'
template_field = '@@REDIS_CLUSTER@@'


with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as nsf:
    ns = nsf.read()


def getClusterIp(services):
    return services is None and '' or services.spec.cluster_ip


def updateConfig(redis_ip, template_field):
    if len(redis_ip.strip()) == 0:
        return
    with open(confid_template_path) as cf:
        configText = cf.read()
    configText = configText.replace(template_field, redis_ip.strip())
    with open(config_file_path, 'w') as cf:
        cf.seek(0)
        cf.write(configText)
        cf.truncate()
    subprocess.run(['supervisorctl', 'restart', target_program], shell=True, check=True)


def watchService(target_service, template_field):
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()
    events = w.stream(v1.list_namespaced_service,
        'stats',
        field_selector=f'metadata.name={target_service}')
    for event in events:
        if 'object' in event:
            ip = getClusterIp(event.get('object'))
            updateConfig(ip, template_field)


def main():
    watchService(target_service, template_field)


if __name__ == "__main__":
    main()
