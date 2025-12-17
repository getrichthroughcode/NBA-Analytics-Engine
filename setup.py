"""
NBA Analytics Engine - Setup Configuration
==========================================
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nba-analytics-engine",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Full-stack NBA analytics platform with ETL, data warehouse, and ML predictions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/getrichthroughcode/nba-analytics-engine",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nba-etl=src.etl.extractors.nba_extractor:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
