from setuptools import setup

setup(
    name='chia-db',
    packages=['code'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
