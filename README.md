# ec2_snap
Program to take snapshots of your EC2 instances

## About

This project is a demo, and uses boto3 to manage AWS EC2 instance snapshots

## Configuring

ec2_snap uses the configuration and credential files created by the awscli

`aws configure --profile=boto`

## Running

`pipenv run python code/ec2_snap.py <command> <--project-PROJECT>`

*command* is list, start, or stop
*project* is optional
