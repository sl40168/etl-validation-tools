from setuptools import setup, find_packages

setup(
    name="etl-validator",
    version="1.0.0",
    description="DolphinDB ETL Data Validation Tool",
    author="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "dolphindb>=1.30.0",
        "pandas>=1.3.0",
        "retrying>=1.3.3",
    ],
    entry_points={
        "console_scripts": [
            "etl_validator=cli.main:main",
        ],
    },
    python_requires=">=3.8",
)
