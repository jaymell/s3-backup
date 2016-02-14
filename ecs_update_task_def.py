#!/usr/bin/python

import boto3
import yaml
import sys

image_revision = sys.argv[1]
task_def = """
family: photo_mapper
containerDefinitions:
- name: pm-flask
  image: 799617403160.dkr.ecr.us-east-1.amazonaws.com/pm-flask-2:%s
  memory: 512
  cpu: 512
  environment:
  - { name: "USE_S3", value: "true" }
- name: nginx
  image: 799617403160.dkr.ecr.us-east-1.amazonaws.com/pm-nginx:latest
  memory: 256
  cpu: 256
  links:
  - pm-flask
  portMappings:
  - { containerPort: 80, hostPort: 80 }
""" % image_revision

client = boto3.client('ecs', region_name='us-east-1')
task_def_response = client.register_task_definition(**yaml.load(task_def))
task_def_revision = int(task_def_response['taskDefinition']['revision'])

service_def = """ 
cluster: pm
service: pm
desiredCount: 2
taskDefinition: %s
deploymentConfiguration: 
  maximumPercent: 100
  minimumHealthyPercent: 50
  
""" % task_def_response['taskDefinition']['family']

service_response = client.update_service(**yaml.load(service_def))
