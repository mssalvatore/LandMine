import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="landmine",
    version="0.0.1",
    author="Mike Salvatore",
    author_email="mike.s.salvatore@gmail.com",
    description="A simple IDS with a near-zero false positive rate",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mssalvatore/LandMine",
    packages=setuptools.find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security",
    ],
    install_requires=[
        'configobj',
        'pythondialog',
        'psutil',
    ],
    python_requires=">=3",
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
    entry_points={'console_scripts': ['landmine=landmine.landmine:run',
                  'configure=landmine.configuration.configure:run']},
    package_data={'landmine.configuration': ['configspec.ini']},
)
