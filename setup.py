from setuptools import setup, find_packages
from pipupdater import VERSION


def readme():
    return open("README.md", "r").read()


setup(
    name="pipupdater",
    version=VERSION,
    author="Molly Maclachlan",
    author_email="murdo@maclachlans.org.uk",
    description="A small command-line tool for automatically updating outdated pip packages.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/MollyMaclachlan/pipupdater",
    packages=find_packages(),
    install_requires=[
        "smooth_logger >= 1.0.0"
    ],
    entry_points={
        'console_scripts': [
            'pipupdater = pipupdater.pipupdater:entry_point'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    license='AGPLv3+'
)
