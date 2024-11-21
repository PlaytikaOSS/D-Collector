from setuptools import setup, find_packages

__version__ = '0.10'

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="D-Collector",
    version=__version__,
    author="Playtika Ltd.",
    author_email="security@playtika.com",
    description="Collect DNS records from various DNS and cloud providers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Playtika/d-collector",
    packages=find_packages(exclude=['tests*']),
    install_requires=requirements,
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'dcollector=dcollector.main:interactive',
        ],
    },
)
