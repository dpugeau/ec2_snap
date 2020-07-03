# snapshotanalyzer.py (ssa.py)

import boto3     # provides AWS access
import botocore  # needed for error checking around starting/stopping instances
import click

session = boto3.Session(profile_name='boto')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

@click.group()
def cli():
    """ssa manages snapshots"""

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
def list_snapshots(project):
    "List EC2 snapshots"

    instances = filter_instances(project)

    print('Snapshot ID, Volume ID, Instance ID, State, Progress, Start Time')
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(', '.join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime('%c')
                )))
    print('Finished')
    return

@cli.group('volume')
def volume():
    """Commands for volumes"""

@volume.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 volumes"

    instances = filter_instances(project)

    print('Volume ID, Instance ID, State, Size, Type, Encryption')
    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + 'GB',
                v.volume_type,
                v.encrypted and "Encrypted" or "Not Encrypted"
                )))
    print('Finished')
    return

   
@cli.group('instance')
def instance():
    """Commands for instances"""

@instance.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"
    #^^^ is a DocString - used to self document python code

    instances = filter_instances(project)

    print('Instance ID, Type, AZ, State, Platform, Public IP, Project')
    for i in instances:
        # use a dictionary comprehension to parse the key/value pairs from the i (instance data)
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            True and i.platform or 'Linux',
            True and i.public_ip_address or '<no IP>',
            tags.get('Project', "<no project>")))) # use .get to avoid error if no project
    print('Finished')
    return

@instance.command('stop')
@click.option('--project', default=None,
        help='Only instances for project (tag Project:<name>)')
def stop_instances(project):
    "Stop EC2 instances"

    instances = filter_instances(project)

    for i  in instances:
        print('Stopping {0}...'.format(i.id))
        try:
            i.stop()
        except botocore.exception.ClientError as e:
            print('Could not Stop {0}. '.format(i.id) + str(e))
            continue
    return

@instance.command('start')
@click.option('--project', default=None,
        help='Only instances for project (tag Project:<name>)')
def start_instances(project):
    "Start EC2 instances"

    instances = filter_instances(project)

    for i  in instances:
        print('Starting {0}...'.format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print('Could not start {0}. '.format(i.id) + str(e))
            continue
    return

@instance.command('snapshot')
@click.option('--project', default=None,
        help='Only instances for project (tag Project:<name>)')
def create_snapshots(project):
    "Create snapshots for EC2 instances"

    instances = filter_instances(project)

    for i  in instances:
        print('Processing Instance ID: {0}'.format(i.id), ' - Stopping... ')
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            print('Starting snapshot of volume ID: {0} ...'.format(v.id))
            v.create_snapshot(Description='Created by SnapshotAnalyzer')
        print('Starting instance...')
        i.start()
        i.wait_until_running()
    print('Finished')
    return


if __name__ == '__main__':
    cli()
