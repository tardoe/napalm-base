"""setup.py file."""
import uuid

from setuptools import setup, find_packages
try: # support pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # pip <= 9.0.3
    from pip.req import parse_requirements

__author__ = 'David Barroso <dbarrosop@dravetech.com>'

install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())
reqs = [str(ir.req) for ir in install_reqs]


setup(
    name="napalm-base",
    version='1.0.0',
    packages=find_packages(),
    author="David Barroso, Kirk Byers, Mircea Ulinic",
    author_email="dbarrosop@dravetech.com, ping@mirceaulinic.net, ktbyers@twb-tech.com",
    description="Network Automation and Programmability Abstraction Layer with Multivendor support",
    classifiers=[
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    url="https://github.com/napalm-automation/napalm-base",
    include_package_data=True,
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'cl_napalm_configure=napalm_base.clitools.cl_napalm_configure:main',
            'cl_napalm_test=napalm_base.clitools.cl_napalm_test:main',
            'cl_napalm_validate=napalm_base.clitools.cl_napalm_validate:main',
            'napalm=napalm_base.clitools.cl_napalm:main',
        ],
    }
)
