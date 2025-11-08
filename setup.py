from setuptools import setup, find_packages

setup(
    name="field-orders",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.2",
        "ccxt>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "field-orders=main:main",
        ],
    },
    author="",
    description="A tool to track and analyze cryptocurrency spot limit orders across multiple exchanges",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
