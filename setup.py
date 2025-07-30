"""
Setup configuration for Clyde - Development Environment Configuration System
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Development Environment Configuration System for Claude"

setup(
    name="clyde",
    version="2.0.0",
    author="Development Team",
    author_email="dev@example.com",
    description="Development Environment Configuration System for Claude",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/clyde",
    packages=find_packages(),
    package_data={
        "": [
            "modules/**/*.md",
            "templates/*.template",
        ]
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "PyYAML>=6.0",
        "Jinja2>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.8.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "clyde=src.cli:cli",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/example/clyde/issues",
        "Source": "https://github.com/example/clyde",
        "Documentation": "https://github.com/example/clyde/blob/main/README.md",
    },
    keywords="development configuration claude ai coding-standards",
)