
from setuptools import setup

setup(
        name='snapshotctl',
        version='0.1',
        author='Don Pugeau',
        author_email='dpugeau@gmail.com',
        description='snapshotctl is a command line tool to help manage EC2 snapshots',
        license='GPLv3+',
        packages=['snapshotctl'],
        url='https://github.com/dpugeau/ec2_snap',
        install_requires=[
            'click',
            'boto3'
        ],
        entry_points='''
        [console_scripts]
        snapctl=snapshotctl.ssc:cli
        ''')
