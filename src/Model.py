from Base import SMObject


class Model(SMObject):

    def __init__(self, model_name):
        self.name = model_name


    def create_model(self, estimator, update=False, instance_size='ml.m5.large', **kwargs):
        if update:
            print(f'Deleting/Recreating model {self.name}')
            try:
                self.sm_session.delete_model(self.name)
            except:
                print(f'No Model named {self.name}. Continuing on to creation.')

        model = estimator.create_model(name=self.name, role=self.role, vpc_config_override=self.vpc_config, **kwargs)
        model._create_sagemaker_model(instance_size)
        
        print(f"Model {self.name} has been created\n. Instance size: {instance_size}\n vpc: {self.vpc_config}")
        return model