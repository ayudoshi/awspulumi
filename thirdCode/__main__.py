#in userdata.sh file on line 7 add your bucket name 

#Created a variable and stored the amazon linux ami
 
amzn_linux_2023_ami = aws.ec2.get_ami(most_recent=True,
    owners=["amazon"],
    filters=[aws.ec2.GetAmiFilterArgs(
        name="name",
        values=["al2023-ami-2023.*-x86_64"],
    )])

#Created security group which will allow ingress http traffic and ssh traffic from anywhere and egress traffic to anywhere

sghttp = aws.ec2.SecurityGroup("sgHttpShh",

    description="Allow http traffic and ssh",
    vpc_id=main.id,
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        description="SSH from anywhere",
        from_port=22,
        to_port=22,
        protocol="tcp",
        cidr_blocks=["0.0.0.0/0"],
    ),
    aws.ec2.SecurityGroupIngressArgs(
        description="HTTP from anywhere",
        from_port=80,
        to_port=80,
        protocol="tcp",
        cidr_blocks=["0.0.0.0/0"],
    )],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
    )],
    tags={
        "Name":"IacSgHttp",
    }
)

#Created s3 bucket read only policy 

S3Role = aws.iam.Role("S3ReadOnly",
    assume_role_policy=json.dumps({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
    }),
    managed_policy_arns=["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"],
    tags={
        "Name": "IacS3ReadOnly",
    })

with open('./userdata.sh', 'r') as user_data_file:
    user_data = user_data_file.read()

# instancePub1a = aws.ec2.Instance("InstancePub1a",
#     ami=amzn_linux_2023_ami.id,
#     instance_type="t2.micro",
#     subnet_id=subPub1a,
#     security_groups=[sghttp],
#     iam_instance_profile=S3Role,
#     user_data=base64.b64encode(user_data.encode()).decode(),
#     tags={
#         "Name":"IacPub1aInstance",
#     })

#Created a launch template
launchTemp = aws.ec2.LaunchTemplate("launchTemp",
    image_id=amzn_linux_2023_ami.id,
    instance_type="t2.micro",
    vpc_security_group_ids=[sghttp.id],
    iam_instance_profile=aws.ec2.LaunchTemplateIamInstanceProfileArgs(
            name=S3Role.name
        ),
    user_data=base64.b64encode(user_data.encode()).decode(),
    tags={
        "Name":"IacLT",
    } 
)

#Created an autoscaling group with the above launch template
autoScalingGr = aws.autoscaling.Group("autoScalingGr",
    vpc_zone_identifiers=[subPub1a.id,subPub1b.id],
    desired_capacity=1,
    max_size=3,
    min_size=0,
    launch_template=aws.autoscaling.GroupLaunchTemplateArgs(
        id=launchTemp.id,
        version="$Latest",
    ),
)

scalingPolicy = aws.autoscaling.Policy("scalingPolicy",
                                        autoscaling_group_name=autoScalingGr,
                                        policy_type="TargetTrackingScaling",
                                        enabled=True,
                                        target_tracking_configuration=aws.autoscaling.PolicyTargetTrackingConfigurationArgs(
                                            predefined_metric_specification=aws.autoscaling.PolicyTargetTrackingConfigurationPredefinedMetricSpecificationArgs(
                                                predefined_metric_type="ASGAverageCPUUtilization",
                                                ),
                                            target_value=50,),
                                        )

loadBalancer = aws.lb.LoadBalancer("IacLoadBalancer",
    internal=False,
    load_balancer_type="application",
    security_groups=[sghttp],
    subnets=[subPub1a,subPub1b],
    tags={
        "Name": "IacLB",
    })
