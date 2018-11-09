import io
import re
from setuptools import setup

with io.open("src/ssm_config/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r"__version__ = \'(.*?)\'", f.read()).group(1)

setup(
    name="ssm-config",
    version=version,
    license="MIT",
    author="Jacopo Sabbatini",
    author_email="dedalusj@gmail.com",
    description="Python package to load environment configuration from YAML files "
                "supporting overriding from environment variables and AWS SSM",
    packages=["ssm_config"],
    package_dir={'': 'src'},
    python_requires=">=3.4",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)