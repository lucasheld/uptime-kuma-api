from setuptools import setup, find_packages

setup(
    name="uptimekumaapi",
    version="0.0.0",
    packages=find_packages(),
    install_requires=[
        "python-socketio==5.6.0",
        "requests==2.28.1",
        "websocket-client==1.3.3",
    ],
)
