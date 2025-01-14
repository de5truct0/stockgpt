from setuptools import setup, find_packages

setup(
    name="stockgpt-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'yfinance>=0.2.0',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'pandas-datareader>=0.10.0',
        'anthropic>=0.3.0',
        'beautifulsoup4>=4.12.0',
        'requests>=2.31.0',
        'rich>=13.0.0',
    ],
    entry_points={
        'console_scripts': [
            'stockgpt=src.stockgpt:main',
        ],
    },
    python_requires='>=3.8',
) 