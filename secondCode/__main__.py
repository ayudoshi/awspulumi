import pulumi
import pulumi_aws as aws

#Create a VPC
main = aws.ec2.Vpc("main",
    cidr_block="10.0.0.0/16",
    tags={
        "Name": "IacVpc",
    })

available = aws.get_availability_zones(state="available")

#Create four subnet in two availabilty zones one public and one priavte in each zone
subPub1a = aws.ec2.Subnet("subPub1a",
    vpc_id=main.id,
    cidr_block="10.0.1.0/24",
    availability_zone=available.names[0],
    tags={
        "Name": "IacPublic-1A",
    })

subPvt1a = aws.ec2.Subnet("subPvt1a",
    vpc_id=main.id,
    cidr_block="10.0.2.0/24",
    availability_zone=available.names[0],
    tags={
        "Name": "IacPrivate-1A",
    })

subPub1b = aws.ec2.Subnet("subPub1b",
    vpc_id=main.id,
    cidr_block="10.0.3.0/24",
    availability_zone=available.names[1],
    tags={
        "Name": "IacPublic-1B",
    })


subPvt1b = aws.ec2.Subnet("subPvt1b",
    vpc_id=main.id,
    cidr_block="10.0.4.0/24",
    availability_zone=available.names[1],
    tags={
        "Name": "IacPrivate-1B",
    })


#Create an internet gateway for public subnets to access internet

gw = aws.ec2.InternetGateway("gw",
    vpc_id=main.id,
    tags={
        "Name": "IacGateWay",
    })

#Assign internet gateway to main route table
mainrt = aws.ec2.DefaultRouteTable("mainrt",
    default_route_table_id=main.default_route_table_id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=gw.id,
        ),
    ],
    tags={
        "Name":"IacMainPubRT"
    }
)

#Create a route table for private subnets

privatert = aws.ec2.RouteTable("privatert",
    vpc_id=main.id,
    tags={
        "Name": "IacPrivRT",
    })


#Assigning route table to private subnets

rtassociationpt1a = aws.ec2.RouteTableAssociation("rtAssociationpt1a",
    subnet_id=subPvt1a,
    route_table_id=privatert.id)

rtassociationpt1b = aws.ec2.RouteTableAssociation("rtAssociationpt1b",
    subnet_id=subPvt1b,
    route_table_id=privatert.id)