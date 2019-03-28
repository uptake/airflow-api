from setuptools import setup
import imp
import os

version = imp.load_source('airflowapi.version', os.path.join('airflowapi', 'version.py')).version

setup_requires = ['pytest-runner']
test_requires = ['pytest']
install_requires = [
    # Api
    'flask-restplus',
    # Airflow
    'apache-airflow[crypto, postgres]==1.10.1'
]


setup(
    name="airflowapi",
    version=version,
    author="zack3241",
    author_email="zmjlawson@gmail.com",
    url='https://github.com/UptakeOpenSource/airflow-api',
    description="A package containing an Apache Airflow plugin for an integrated RESTful API",
    packages=[
        'airflowapi',
        'airflowapi.v1'
    ],
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
      "test": setup_requires + test_requires + install_requires
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 3.6'
    ],
    setup_requires=setup_requires,
    tests_require=test_requires
)
