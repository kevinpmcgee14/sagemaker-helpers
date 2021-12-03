from sagemaker.session import production_variant
from Base import SMObject



class ProducitonVariant(SMObject):

    def __init__(self):
        pass

    def create_production_variant(model_name, instance_type, initial_instance_count, variant_name, initial_weight=0.):
        try:
            assert model_name is not None
        except AssertionError:
            pass
        
        pv = production_variant(model_name=model_name,
                                instance_type=instance_type,
                                initial_instance_count=initial_instance_count,
                                variant_name=variant_name,
                                initial_weight=initial_weight)
        print(f"Production Variant {variant_name} for model  {model_name} has been created.")
        return pv
