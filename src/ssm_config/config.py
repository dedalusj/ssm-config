import os
import re
from typing import Dict, Optional, TextIO, Union

import boto3
from botocore.exceptions import ClientError
import yaml


class ConfigLoader(yaml.SafeLoader):
    _env_pattern = re.compile(r'^(.*)<%= ENV\[\'(.*)\'\] %>(.*)$')
    _ssm_pattern = re.compile(r'^(.*)<%= SSM\[\'(.*)\'\] %>(.*)$')

    def __init__(self, stream):
        super().__init__(stream)
        self.add_implicit_resolver("!pathenv", self._env_pattern, None)
        self.add_constructor('!pathenv', self._pathenv_constructor)
        self.add_implicit_resolver("!pathssm", self._ssm_pattern, None)
        self.add_constructor('!pathssm', self._pathssm_constructor)

    @staticmethod
    def _pathenv_constructor(loader: 'ConfigLoader', node: yaml.ScalarNode) -> str:
        value = loader.construct_scalar(node)
        pre_path, env_var, post_path = ConfigLoader._env_pattern.match(value).groups()
        return pre_path + os.environ[env_var] + post_path

    @staticmethod
    def _pathssm_constructor(loader: 'ConfigLoader', node: yaml.ScalarNode) -> str:
        value = loader.construct_scalar(node)
        pre_path, ssm_path, post_path = ConfigLoader._ssm_pattern.match(value).groups()
        client = boto3.client('ssm')
        try:
            response = client.get_parameter(Name=ssm_path, WithDecryption=True)
            return pre_path + response['Parameter']['Value'] + post_path
        except ClientError as e:
            if e.response['Error']['Code'] == 'ParameterNotFound':
                raise ValueError(f'Could not find SSM parameter {ssm_path}')
            raise


def load(stream: Union[str, TextIO]) -> Dict:
    return yaml.load(stream, Loader=ConfigLoader)


def load_env(stream: Union[str, TextIO], env: Optional[str] = None) -> Dict:
    full_config = yaml.load(stream, Loader=ConfigLoader)
    if env is None:
        env = os.getenv('ENVIRONMENT', 'dev')
    if env not in full_config:
        raise ValueError(f'Unknown environment {env}')
    return full_config[env]
