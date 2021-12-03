from setuptools import setup, find_packages

setup(
    name='sm_helpers', 
    version='0.0.1', 
    packages=find_packages(),
    install_requires=[
        'sagemaker==2.69.0',
        'boto3==1.20.16'
    ],

    )
