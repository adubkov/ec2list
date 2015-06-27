#!/usr/bin/env python

import boto
import boto.ec2
import logging

from multiprocessing.pool import ThreadPool as Pool

def get_profiles():
    """Return list of all regions."""
    result = []
    for profile in boto.config.sections():
        if profile.strip().lower().startswith('profile'):
            result.append(profile.strip().lower()[8:])
    return result

def get_instances(kwargs):
    """Print list of instances in specific account and region."""
    result = []
    region = kwargs.get('region')
    profile = kwargs.get('profile')
    try:
        ec2 = boto.ec2.connect_to_region(region, profile_name=profile)
        log.info('Getting list of instances from %s: %s', profile, region)
        # Get only running instances
        reservations = ec2.get_all_instances(filters={'instance-state-name':'running'})
        for reservation in reservations:
            for instance in reservation.instances:
                # This result will be returned for future use
                result.append(instance.tags.get('Name', instance.id))
                print('{instance_id},{name},{private_ip},{public_ip},{instance_type},{region},{profile}'.format(
                    instance_id = instance.id,
                    name = instance.tags.get('Name'),
                    private_ip = instance.private_ip_address,
                    public_ip = instance.ip_address,
                    instance_type = instance.instance_type,
                    region = region,
                    profile = profile,
                    ))
    except boto.exception.EC2ResponseError as e:
        log.error('Error list instances in %s: %s (%s)', profile, region, e)
    finally:
        return result

def run_parallel(func, args, threads, callback):
    """Run processing arguments with function in multiple threads."""
    pool = Pool(processes=threads)
    pool.map_async(func, args, callback=callback)
    pool.close()
    pool.join()

def main():
    # Fill list of profile\region pairs
    queue = []
    instances = []
    for profile in get_profiles():
        for region in boto.ec2.regions():
            queue.append({'profile':profile, 'region':region.name})

    # Run processing accounts and regions in parallel threads
    run_parallel(get_instances, queue, 50, instances.extend)

    # Return list of all instances name or id, if name is not assigned
    instances = [j for i in instances for j in i]

if __name__ == '__main__':
    logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s][%(levelname)s] %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S')
    logging.getLogger('boto').setLevel(logging.CRITICAL)
    logging.getLogger(__name__).setLevel(logging.CRITICAL)
    log = logging.getLogger(__name__)

    main()
