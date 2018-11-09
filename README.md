# ssm-config

[![Build Status](https://travis-ci.com/dedalusj/ssm-config.svg?branch=master)](https://travis-ci.com/dedalusj/ssm-config) [![codecov](https://codecov.io/gh/dedalusj/ssm-config/branch/master/graph/badge.svg)](https://codecov.io/gh/dedalusj/ssm-config)

Python package to load environment configuration from YAML files supporting overriding from environment variables and AWS SSM

Image you have an environment variable `USERNAME=prod_user`, an SSM parameter `/prod/password=prod_password` and the following YAML config file

```yaml
default: &default
  username: a_user
  password: a_password
  host: a_host.com
prod:
  <<: *default
  username: <%= ENV['USERNANE'] %>
  password: <%= SSM['/prod/password'] %>
```

then the parsed config for prod will be 

```yaml
prod:
  username: prod_user
  password: prod_password
  host: a_host.com
```

The configuration can be loaded with

```python
from ssm_config import load_env

dev_config = load_env('config.yml')  # load the config for the dev environment by default
staging_config = load_env('config.yml', env='staging')  # manually force to load the staging environment config
```
