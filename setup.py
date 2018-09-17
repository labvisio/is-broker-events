from setuptools import setup, find_packages

setup(
    name='is_broker_events',
    version='0.0.3',
    description='',
    url='http://github.com/labviros/is-broker-events',
    author='labviros',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'is-broker-events=is_broker_events.service:main',
        ],
    },
    zip_safe=False,
    install_requires=[
        'is-wire==1.1.2',
        'is-msgs==1.1.5',
        'requests==2.19.1',
    ],
)
