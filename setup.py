from setuptools import setup
from codecs import open
import os
import sys

# "setup.py publish" shortcut.
if sys.argv[-1] == "publish":
    os.system("rm dist/*")
    os.system("python setup.py sdist")
    os.system("twine upload dist/*")
    sys.exit()

info = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "uptime_kuma_api", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), info)

setup(
    name=info["__title__"],
    version=info["__version__"],
    description="A python wrapper for the Uptime Kuma WebSocket API",
    url="https://github.com/lucasheld/uptime-kuma-api",
    author=info["__author__"],
    author_email="lucasheld@hotmail.de",
    license=info["__license__"],
    packages=["uptime_kuma_api"],
    python_requires=">=3.6, <4",
    install_requires=["python-socketio[client]>=5.0.0"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries"
    ]
)
