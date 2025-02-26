from setuptools import setup, find_packages

setup(
    name="coinbase-order-tracker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.2",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "coinbase-order-tracker=main:main",
        ],
    },
    author="Coinbase Order Tracker",
    description="A tool to track and analyze Coinbase spot limit orders",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
