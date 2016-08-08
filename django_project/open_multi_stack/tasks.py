from celery import task
from time import sleep
from datetime import datetime
from novaclient.client import Client
from novaclient import exceptions as nova_exceptions
import string
import random
import time
import logging

logger = logging.getLogger(__name__)

def get_nova_credentials(account):
    d = {}
    d['version'] = account.version
    d['username'] = account.username
    d['api_key'] = account.password
    d['auth_url'] = account.auth_url
    d['project_id'] = account.tenant_name
    d['region_name'] = account.region_name
    return d

@task

def create_openstack_instance(queue_record):
    from open_multi_stack.models import Account, Instance, Queue

    if queue_record.status != Queue.STATUS_REQUEST:
        return

    # update queue record status (RECIVE)
    queue_record.status = Queue.STATUS_RECIVE
    queue_record.save()

    for account in Account.objects.all():
        try:
            credentials = get_nova_credentials(account)
            nova_client = Client(**credentials)
            image = nova_client.images.find(name="vmi-debian-8-amd64")
            flavor = nova_client.flavors.find(name="g-1gb")
            key_name = random_str = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(10)])
            keypair = nova_client.keypairs.create(name=key_name)
            
            # update queue record status (BOOT)
            queue_record.status = Queue.STATUS_BOOT
            queue_record.save()

            instance = nova_client.servers.create(
                    name="open multi stack instance",
                    image=image,
                    flavor=flavor,
                    key_name=key_name,
                    security_groups=["gncs-ipv4-all"]
            )
            status = instance.status
            while status == 'BUILD':
                time.sleep(5)
                # Retrieve the instance again so the status field updates
                instance = nova_client.servers.get(instance.id)
                status = instance.status
           
            # insert instance record
            instance_record = Instance(
                instance_id= instance.id,
                name=instance.name,
                ip_addr = instance.interface_list()[0].fixed_ips[0]['ip_address'],
                key_name = key_name,
                key_raw = keypair.private_key,
                account=account
            )
            instance_record.save()
            
            # relate instance record and queue record
            queue_record.instance =instance_record
            queue_record.save()

            # update queue record status (RUN)
            queue_record.status = Queue.STATUS_RUN
            queue_record.save()
 
            break
        except (nova_exceptions.BadRequest, nova_exceptions.Forbidden) as ex:
            logger.info(ex.message)
           # update queue record status (FAILED)
            queue_record.status = Queue.STATUS_FAILED
            queue_record.save()

@task

def delete_openstack_instance(queue_record):
    from open_multi_stack.models import Account, Instance, Queue
    instance_record = queue_record.instance

    if instance_record is None:
        return

    account_record = instance_record.account

    credentials = get_nova_credentials(account_record)
    nova_client = Client(**credentials)
    nova_client.servers.delete(instance_record.instance_id) 
    nova_client.keypairs.delete(instance_record.key_name)
    instance_record.delete()


