#!/usr/bin/python

import troposphere as tr
from troposphere import ec2
import yaml
import netaddr
import argparse
import sys

MASK = 24

class VPC:
    def __init__(self, Name, CidrBlock):
        self.name = Name
        self.network = netaddr.IPNetwork(CidrBlock)

parser = argparse.ArgumentParser()
parser.add_argument("yaml_file")
args = parser.parse_args()

stack_id = tr.Ref('AWS::StackId')
region = tr.Ref('AWS::Region')
stack_name = tr.Ref('AWS::StackName')
app_tag = tr.Tags(Application=stack_id)

# object representing CloudFormation template
t = tr.Template()
t.add_version('2010-09-09')
t.add_description('CloudFormation template for VPC and Subnets')

# yaml file as dict
try: 
	with open(args.yaml_file) as f:
		yaml_file = yaml.load(f)
except Exception as e:
	print('Failed to open yaml: %s' % e)
	sys.exit(1)

# vpc:
vpc = ec2.VPC(yaml_file['VPC']['Name'], CidrBlock=yaml_file['VPC']['CidrBlock'], Tags=app_tag)
t.add_resource(vpc)

# gateway:
gw = ec2.InternetGateway('InternetGateway',Tags=app_tag)
t.add_resource(gw)

# attachment, or whatever:
attach = ec2.VPCGatewayAttachment('AttachGateway',VpcId=vpc,InternetGatewayId=gw)
t.add_resource(attach)

# route tables:
rt_list = []
for route_table in yaml_file['RouteTables']:
	rt = ec2.RouteTable(route_table['Name'], VpcId=vpc, Tags=app_tag)
	rt_list.append(rt)
	t.add_resource(rt)
	# add public route if it's public:
	if route_table['Scope'].lower() == 'public':
		route = ec2.Route('Route',
							DependsOn = 'AttachGateway',
							GatewayId = gw,
							DestinationCidrBlock = '0.0.0.0/0',
							RouteTableId = rt
					)
		t.add_resource(route)
		
# subnets:
rac_vpc = VPC(**yaml_file['VPC'])
subnet_generator = rac_vpc.network.subnet(MASK)
for subnet in yaml_file['Subnets']:
    sub = ec2.Subnet(subnet['Name'], 
						VpcId = vpc, 
						CidrBlock = subnet_generator.next().__str__(), 
						Tags = app_tag
					)
    t.add_resource(sub)
	# subnet-route-table associations:
	sub_rt_assoc = ec2.subnetRouteTableAssociation(
							'SubnetRouteTableAssociation', 
							SubnetId = sub, 
							RouteTableId=Ref(routeTable)
						)
	t.add_resource(
# render the beast in json:
print(t.to_json())
