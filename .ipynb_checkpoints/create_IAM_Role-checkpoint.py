import boto3
import time
import configparser
from botocore.exceptions import ClientError
import pandas as pd
import json


config = configparser.ConfigParser()
config.optionxform = str
config.read('dwh.cfg')

iam = boto3.client('iam',
                   aws_access_key_id=config.get('AWS', 'KEY'),
                   aws_secret_access_key=config.get('AWS', 'SECRET'),
                   region_name='us-west-2'
                  )

def create_iam_role():
    #1.1 Create the role, 
    try:
        print("1.1 Creating a new IAM Role") 
        dwhRole = iam.create_role(
            Path='/',
            RoleName=config.get('DWH','DWH_IAM_ROLE_NAME'),
            Description = "Allows Redshift clusters to call AWS services on your behalf.",
            AssumeRolePolicyDocument=json.dumps(
                {'Statement': [{'Action': 'sts:AssumeRole',
                   'Effect': 'Allow',
                   'Principal': {'Service': 'redshift.amazonaws.com'}}],
                 'Version': '2012-10-17'})
        )    
    except Exception as e:
        print(e)


    print("1.2 Attaching Policy")

    iam.attach_role_policy(RoleName=config.get('DWH','DWH_IAM_ROLE_NAME'),
                           PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
                          )['ResponseMetadata']['HTTPStatusCode']

    print("1.3 Get the IAM role ARN")
    roleArn = iam.get_role(RoleName=config.get('DWH','DWH_IAM_ROLE_NAME'))['Role']['Arn']
    
    config.set('IAM_ROLE', 'ARN', roleArn)
    config.write(open('dwh.cfg', 'w'))
    
    print(roleArn)

def main():
    create_iam_role()
    

if __name__=="__main__":
    main()