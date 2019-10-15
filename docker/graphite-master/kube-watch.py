import subprocess, asyncio

from kubernetes import client, config, watch


confid_template_path = '/opt/graphite/webapp/graphite/local_settings.py.template'
config_file_path = '/opt/graphite/webapp/graphite/local_settings.py'
target_program = 'graphite-webapp'
target_service = 'redis-tags'
template_field = '@@REDIS_CLUSTER@@'


with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as nsf:
    ns = nsf.read()


def get_cluster_ip(services):
    return services is None and '' or services.spec.cluster_ip


def get_endpoint_addresses(endpoints):
    if endpoints is None:
        return ''
    else:
        addresses = [a for s in endpoints.subsets for a in s.addresses]
        return addresses.join(',')


class TemplateConfig(object):
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest
        self.cfg = ''
        self.load()
    
    def load(self):
        with open(src) as cf:
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
        ns,
        field_selector=f'metadata.name={target_service}')
    for event in events:
        if 'object' in event:
            yield get_cluster_ip(event.get('object'))


async def watch_endpoints(target_endpoints, template_field):
    v1 = client.CoreV1Api()
    w = watch.Watch()
    events = w.stream(v1.list_namespaced_endpoint,
        ns,
        field_selector=f'metadata.name={target_endpoints}')
    for event in events:
        if 'object' in event:
            yield get_endpoint_addresses(event.get('object'))


async def watch_kubes(cfg, svc_args, ept_args):
    while True:
        svc_ip, ept_ips = await asyncio.gather(
            watch_service(*svc_args),
            watch_endpoints(*ept_args),
            )
        cfg.update_config(*svc_args)
        cfg.update_config(*ept_args)
        cfg.write()
        restart_program()


def main():
    config.load_incluster_config()
    asyncio.run(watch_service(target_service, template_field))


if __name__ == "__main__":
    main()
