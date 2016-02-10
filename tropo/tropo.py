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
vpc_ref = tr.Ref(vpc)

# gateway:
gw = ec2.InternetGateway('InternetGateway',Tags=app_tag)
t.add_resource(gw)
gw_ref = tr.Ref(gw)

# attachment, or whatever:
attach = ec2.VPCGatewayAttachment('AttachGateway',VpcId=vpc_ref,InternetGatewayId=gw_ref)
t.add_resource(attach)
attach_ref = tr.Ref(attach)

# route tables:
### HOW continue to uniquely identify
### route_tables after definition in a loop;
### should they 1) be converted from array to object
### here, 2) be put into yaml file as assoc array to
### begin with; 3) something else, ie maybe time 
### to start thinking about a larger object structure
### for the entire vpc
route_tables = yaml_file['RouteTables']
for route_table in route_tables:
	rt = ec2.RouteTable(route_table['Name'], VpcId=vpc_ref, Tags=app_tag)
	t.add_resource(rt)
	rt_ref = tr.Ref(rt)
	rt_refs.update(rt_ref)
	# add public route if it's public:
	if route_table['Scope'].lower() == 'public':
		route = ec2.Route('Route',
							DependsOn = 'AttachGateway',
							GatewayId = gw_ref,
							DestinationCidrBlock = '0.0.0.0/0',
							RouteTableId = rt_ref
					)
		t.add_resource(route)
		route_ref = tr.Ref(route)
		
# subnets:
vpc_obj = VPC(**yaml_file['VPC'])
subnet_generator = vpc_obj.network.subnet(MASK)
subnets = yaml_file['Subnets']
for subnet in subnets:
	sub = ec2.Subnet(subnet['Name'],VpcId = vpc_ref,CidrBlock = subnet_generator.next().__str__(),Tags = app_tag)
	t.add_resource(sub)
	sub_ref = tr.Ref(sub)
	# put associated route table in var so it can be accessed easier:
	sub_rt = subnet['Routetable']
	# subnet-route-table associations:
	sub_rt_assoc = ec2.SubnetRouteTableAssociation('%sAssoc' % subnet['Name'],SubnetId=sub_ref,RouteTableId=rt_refs[sub_rt])
	t.add_resource(sub_rt_assoc)
	sub_rt_assoc_ref = tr.Ref(sub_rt_assoc)

# render the beast in json:
print(t.to_json())
