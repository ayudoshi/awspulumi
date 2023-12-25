"""An AWS Python Pulumi program"""

import pulumi
from pulumi_aws import s3
import json

# Create an AWS resource (S3 Bucket)
bucket = s3.Bucket("my-bucket",
    website=s3.BucketWebsiteArgs(
        index_document="index.html",
    ),
)

bucket_object = s3.BucketObject(
    'index.html',
    bucket=bucket.id,
    source=pulumi.FileAsset('index.html'),
    content_type='text/html',
    acl='public-read',
    # opts=pulumi.ResourceOptions(depends_on=[public_access_block]),
)


# Export the name of the bucket
pulumi.export('bucket_name', bucket.id)
pulumi.export('bucket_endpoint', pulumi.Output.concat('http://', bucket.website_endpoint))