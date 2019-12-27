import os, subprocess, asyncio

from kubernetes import client, config, watch


DEFAULT_SERVICE=os.getenv('REDIS_SERVICE', 'redis-tags.stats.svc')
DEFAULT_ENDPOINT=os.getenv('GRAPHITE_NODES', 'graphite-node.stats.svc')
config_template_path = '/opt/graphite/webapp/graphite/local_settings.py.template'
config_file_path = '/opt/graphite/webapp/graphite/local_settings.py'
target_program = 'graphite-webapp'
target_service = 'redis-tags'
target_endpoint = 'graphite-node'
template_service_field = '@@REDIS_CLUSTER@@'
template_endpoint_field = '@@GRAPHITE_NODES@@'


with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as nsf:
    namespace = nsf.read()


def get_cluster_ip(services):
    return services is None and DEFAULT_SERVICE or services.spec.cluster_ip


def get_endpoint_addresses(endpoints):
    if endpoints is None:
        return DEFAULT_ENDPOINT
    else:
        addresses = [f"'{a.ip}'" for s in endpoints.subsets for a in s.addresses]
        if not addresses:
            return DEFAULT_ENDPOINT
        return ','.join(addresses)


class TemplateConfig(object):
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest
        self.cfg = ''
        self.load()
    
    def load(self):
        with open(self.src) as cf:
            self.cfg = cf.read()
    
    def update_config(self, template_value, template_field):
        if len(template_value.strip()) == 0:
            return
        self.cfg = self.cfg.replace(template_field, template_value.strip())
    
    def write(self):
        with open(self.dest, 'w') as cf:
            cf.write(self.cfg)
        self.load()


def restart_program(target_program):
    subprocess.run(f'supervisorctl restart {target_program}', shell=True, check=True)


async def watch_service(target_service, template_field):
    v1 = client.CoreV1Api()
    w = watch.Watch()
    events = w.stream(v1.list_namespaced_service,
        namespace,
        field_selector=f'metadata.name={target_service}')
    for event in events:
        if 'object' in event:
            yield get_cluster_ip(event.get('object'))


async def watch_endpoints(target_endpoints, template_field):
    v1 = client.CoreV1Api()
    w = watch.Watch()
    events = w.stream(v1.list_namespaced_endpoints,
        namespace,
        field_selector=f'metadata.name={target_endpoints}')
    for event in events:
        if 'object' in event:
            yield get_endpoint_addresses(event.get('object'))


async def watch_kubes(cfg, svc_args, ept_args):
    svc_itr = watch_service(*svc_args)
    ept_itr = watch_endpoints(*ept_args)
    while True:
        svc_ip, ept_ips = await asyncio.gather(
            svc_itr.__anext__(),
            ept_itr.__anext__(),
            )
        cfg.update_config(svc_ip, template_service_field)
        cfg.update_config(ept_ips, template_endpoint_field)
        cfg.write()
        restart_program(target_program)


def main():
    config.load_incluster_config()
    cfg = TemplateConfig(config_template_path, config_file_path)
    svc_args, ept_args = (
        (target_service, template_service_field),
        (target_endpoint, template_endpoint_field))
    asyncio.run(watch_kubes(cfg, svc_args, ept_args))


if __name__ == "__main__":
    main()
