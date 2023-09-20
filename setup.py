from setuptools import setup

setup(
    name='is_broker_events',
    version='0.0.4',
    description='',
    url='http://github.com/labvisio/is-broker-events',
    author='labvisio',
    license='MIT',
    packages=[
        'is_broker_events',
        'is_broker_events.conf',
    ],
    package_dir={'': '.'},
    entry_points={
        'console_scripts': [
            'is-broker-events=is_broker_events.service:main',
        ],
    },
    zip_safe=False,
    install_requires=[
        'is-wire==1.2.1',
        'is-msgs==1.1.18',
        'requests==2.31.0',
        'six==1.16.0',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
        'Programming Language :: Python :: 3 :: Only',
    ],
)
