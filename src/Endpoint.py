import botocore
from ProductionVariant import ProducitonVariant
from Base import SMObject
from datetime import datetime

class Endpoint(SMObject):

    def __init__(self, endpoint_name):
        self.super().__init__()
        self.endpoint_name = endpoint_name
        try:
            self.endpoint_description = self.sm_session.sagemaker_client.describe_endpoint(EndpointName=self.endpoint_name)
            self.config = self.sm_session.sagemaker_client.describe_endpoint_config(EndpointConfigName=self.endpoint_description['EndpointConfigName'])
        except botocore.exceptions.ClientError:
            self.endpoint_description = None
            self.config = {}
        self.variants = self.config.get('ProductionVariants', [])
        self.autoscaling = self.AutoScaling()


    def attach_variants(self, variants, clear=False):
        if clear:
            new_variants = variants
        else:
            new_variants = self.variants + variants
        
        original_key_mapping = {v['VariantName']: v for v in self.variants}
        variant_key_mapping = {v['VariantName']: v for v in new_variants}     
                        
        total_weight = sum([v['InitialVariantWeight'] for _, v in variant_key_mapping.items()])
        if total_weight != 1.:
            weight_configuration = {vname: v['InitialVariantWeight'] for vname, v in variant_key_mapping.items()}
            return f"Cannot set production variants with a total weight != 1. Please check the variants and set the weights as needed: {weight_configuration}"
        
        
        removed_variants = set(original_key_mapping) - set(variant_key_mapping)
        
        for v in removed_variants:
            try:
                self.autoscaling.deregister_scalable_target(self.endpoint_name, v)
            except Exception as e:
                print(e)
    
        final_variants = [pv for pv in variant_key_mapping.values()]

        self.create_config_from_existing(new_production_variants=final_variants)
        

    def create_config_from_existing(self, existing_config_name=None, **kwargs):
        if not existing_config_name:
            existing_config_name = self.endpoint_description['EndpointConfigName']
        new_config_name = f"{self.endpoint_name}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
        
        self.sm_session.create_endpoint_config_from_existing(existing_config_name, new_config_name, **kwargs)
        new_config = self.sm_session.sagemaker_client.describe_endpoint_config(EndpointConfigName=new_config_name)
        return new_config

    def deploy_config(self, config_name, wait=False):
        
        print(f'Deploying the following configuration for endpoint {self.endpoint_name}:\n {config_name}...')
        
        self.sm_session.update_endpoint(self.endpoint_name, config_name, wait=wait)

    def deploy_production_variants(self):
        self.sm_session.endpoint_from_production_variants(
            name=self.endpoint_name,
            production_variants=self.variants
        )
        
    
    class AutoScaling:

        def __init__(self):
            self.autoscaling_client = self.boto3_session.client('application-autoscaling')

        def register_scalable_target(self, variant, minimum=1, maximum=8):
            print('Waiting on endpoint to be in service...')
            waiter = self.sm_session.sagemaker_client.get_waiter('endpoint_in_service')
            waiter.wait(EndpointName=self.endpoint_name)
            print('Endpoint in service. Registering as scalable target.')
            self.autoscaling_client.register_scalable_target(
                ServiceNamespace='sagemaker',
                ResourceId= f'endpoint/{self.endpoint_name}/variant/{variant}',
                ScalableDimension = 'sagemaker:variant:DesiredInstanceCount',
                MinCapacity=minimum,
                MaxCapacity=maximum,
            )
            return self.autoscaling_client.describe_scalable_targets(
                ServiceNamespace='sagemaker',
                ResourceIds= f'endpoint/{self.endpoint_name}/variant/{variant}',
                ScalableDimension = 'sagemaker:variant:DesiredInstanceCount'
            )

        def deregister_scalable_target(self, variant):
            self.autoscaling_client.deregister_scalable_target(
                ServiceNamespace='sagemaker',
                ResourceId=f'endpoint/{self.endpoint_name}/variant/{variant}',
                ScalableDimension = 'sagemaker:variant:DesiredInstanceCount'
            )