import subprocess

from kubernetes import client, config, watch


config_template_path = '/opt/graphite/conf/carbon.conf.template'
config_file_path = '/opt/graphite/conf/carbon.conf'
target_program = 'carbon-relay'
target_endpoints = 'graphite-node'
template_field = '@@GRAPHITE_NODES@@'


with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as nsf:
    namespace = nsf.read()


def get_cluster_ip(services):
    return services is None and '' or services.spec.cluster_ip


def get_endpoint_addresses(endpoints):
    if endpoints is None:
        return ''
    else:
        addresses = [f"'{a}'" for s in endpoints.subsets for a in s.addresses]
        return ','.join(addresses)


def update_config(template_value, template_field):
    if len(template_value.strip()) == 0:
        return
    with open(config_template_path) as cf:
        configText = cf.read()
    configText = configText.replace(template_field, template_value.strip())
    with open(config_file_path, 'w') as cf:
        cf.write(configText)
    subprocess.run(f'supervisorctl restart {target_program}', shell=True, check=True)


def watch_endpoints(target_endpoints, template_field):
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()
    events = w.stream(v1.list_namespaced_endpoint,
        namespace,
        field_selector=f'metadata.name={target_endpoints}')
    for event in events:
        if 'object' in event:
            ip = get_endpoint_addresses(event.get('object'))
            update_config(ip, template_field)


def main():
    watch_endpoints(target_endpoints, template_field)


if __name__ == "__main__":
    main()
