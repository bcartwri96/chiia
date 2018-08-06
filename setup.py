from setuptools import setup

setup(
    name='chia-db',
    packages=['code'],
    allowed_hosts=['*'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
