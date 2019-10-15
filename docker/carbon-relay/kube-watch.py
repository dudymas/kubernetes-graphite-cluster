import subprocess

from kubernetes import client, config, watch


confid_template_path = '/opt/graphite/conf/carbon.conf.template'
config_file_path = '/opt/graphite/conf/carbon.conf'
target_program = 'carbon-relay'
target_endpoints = 'graphite-node'
template_field = '@@GRAPHITE_NODES@@'


with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as nsf:
    namespace = nsf.read()


def getClusterIp(services):
    return services is None and '' or services.spec.cluster_ip


def getAddresses(endpoints):
    if endpoints is None:
        return ''
    else:
        addresses = [a for s in endpoints.subsets for a in s.addresses]
        return addresses.join(',')


def updateConfig(redis_ip, template_field):
    if len(redis_ip.strip()) == 0:
        return
    with open(confid_template_path) as cf:
        configText = cf.read()
    configText = configText.replace(template_field, redis_ip.strip())
    with open(config_file_path, 'w') as cf:
        cf.write(configText)
    subprocess.run(f'supervisorctl restart {target_program}', shell=True, check=True)


def watchEndpoints(target_endpoints, template_field):
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()
    events = w.stream(v1.list_namespaced_endpoint,
        namespace,
        field_selector=f'metadata.name={target_endpoints}')
    for event in events:
        if 'object' in event:
            ip = getAddresses(event.get('object'))
            updateConfig(ip, template_field)


def main():
    watchEndpoints(target_endpoints, template_field)


if __name__ == "__main__":
    main()
