import os

from botocore import exceptions as boto_exceptions
import pytest

from config.config import load, load_env


def test_load_simple_file():
    data = """
    default:
      username: user
      password: password
    prod:
      username: user
      password: password   
    """
    assert load(data) == {'default': {'password': 'password', 'username': 'user'},
                          'prod': {'password': 'password', 'username': 'user'}}


def test_load_file_with_overriding():
    data = """
    default: &default
      username: user
      password: password
    prod:
      <<: *default
      password: prod_password
    """
    assert load(data) == {'default': {'password': 'password', 'username': 'user'},
                          'prod': {'password': 'prod_password', 'username': 'user'}}


def test_load_file_with_env_values(mocker):
    mocker.patch.dict(os.environ, {'USER': 'me'})

    assert load("""
    prod:
      path: <%= ENV['USER'] %>
    """) == {'prod': {'path': 'me'}}

    assert load("""
    prod:
      path: /home/<%= ENV['USER'] %>
    """) == {'prod': {'path': '/home/me'}}

    assert load("""
    prod:
      path: /home/<%= ENV['USER'] %>/src
    """) == {'prod': {'path': '/home/me/src'}}

    assert load("""
    prod:
      path: <%= ENV['USER'] %>/src
    """) == {'prod': {'path': 'me/src'}}


def test_load_file_with_unknown_env_value():
    with pytest.raises(KeyError):
        load("""
        prod:
          path: <%= ENV['UNKNOWN_ENV_VAR'] %>
        """)


def test_load_file_with_ssm_values(mocker):
    mocked_client = mocker.Mock()
    mocked_client.get_parameter.return_value = {'Parameter': {'Value': 'me'}}
    mocked_boto = mocker.patch('config.config.boto3')
    mocked_boto.client.return_value = mocked_client

    assert load("""
        prod:
          path: <%= SSM['/prod/user'] %>
        """) == {'prod': {'path': 'me'}}

    assert load("""
        prod:
          path: /home/<%= SSM['/prod/user'] %>
        """) == {'prod': {'path': '/home/me'}}

    assert load("""
        prod:
          path: /home/<%= SSM['/prod/user'] %>/src
        """) == {'prod': {'path': '/home/me/src'}}

    assert load("""
        prod:
          path: <%= SSM['/prod/user'] %>/src
        """) == {'prod': {'path': 'me/src'}}


def test_load_file_with_invalid_ssm_value(mocker):
    mocked_client = mocker.Mock()
    mocked_client.get_parameter.side_effect = boto_exceptions.ClientError({'Error': {'Code': 'ParameterNotFound'}},
                                                                          'get')
    mocked_boto = mocker.patch('config.config.boto3')
    mocked_boto.client.return_value = mocked_client

    with pytest.raises(ValueError):
        load("""
        prod:
          path: <%= SSM['/prod/unknown_param'] %>
        """)


def test_load_env(mocker):
    data = """
    default: &default
      username: user
      password: password
    dev:
      <<: *default
      password: dev
    staging:
      <<: *default
      password: staging
    prod:
      <<: *default
      password: prod   
    """
    assert load_env(data) == {'username': 'user', 'password': 'dev'}
    assert load_env(data, env='staging') == {'username': 'user', 'password': 'staging'}
    mocker.patch.dict(os.environ, {'ENVIRONMENT': 'prod'})
    assert load_env(data) == {'username': 'user', 'password': 'prod'}


def test_load_unknown_env():
    data = """
    default: &default
      username: user
      password: password
    dev:
      <<: *default
      password: dev
      password: prod   
    """
    with pytest.raises(ValueError):
        load_env(data, env='unknown')
