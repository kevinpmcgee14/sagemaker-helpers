from sagemaker.session import production_variant
from Base import SMObject
from __logging__ import logger


class ProducitonVariant(SMObject):

    def __init__(self, model_name):
        try:
            assert isinstance(model_name, str) and model_name != ''
        except AssertionError:
            self.model_name = model_name

    def create_production_variant(self, instance_type, initial_instance_count, variant_name, initial_weight=0.):        
        pv = production_variant(model_name=self.model_name,
                                instance_type=instance_type,
                                initial_instance_count=initial_instance_count,
                                variant_name=variant_name,
                                initial_weight=initial_weight)
        logger.info(f"Production Variant {variant_name} for model  {model_name} has been created.")
        return pv
