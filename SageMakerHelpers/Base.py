import sagemaker
import boto3
import json


class SMObject(object):

    def __init__(self):
        self.boto3_session = boto3.Session()
        self.sm_session = sagemaker.Session()
        self.region = self.boto3_session.region_name
        self.role = sagemaker.get_execution_role()


    def configure_vpc(self, subnets: list, security_groups: list):
        try:
            assert all(subnets, security_groups)
        except:
            return 'Must have subnets and security groups set'

        self.vpc_config={
            "Subnets": subnets,
            "SecurityGroupIds": security_groups
        }
    
    def configure_vpc_from_secrets(self, subnet_secret, security_group_secret):
        secrets_manager = boto3.client('secretsmanager')
        subnet_info = json.loads(secrets_manager.get_secret_value(SecretId=subnet_secret)['SecretString'])
        security_group_info = json.loads(secrets_manager.get_secret_value(SecretId=security_group_secret)['SecretString'])
        if isinstance(subnet_info, str):
            subnet_info = [subnet_info]
        if isinstance(security_group_info, str):
            security_group_info = [security_group_info]
        self.configure_vpc(subnet_info, security_group_info)
        