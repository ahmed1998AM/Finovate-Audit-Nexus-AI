#!/usr/bin/env python3
"""
Finovate Audit Nexus AI - Setup Script
Enterprise AI Financial Audit & Intelligence Platform
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="finovate-audit-nexus-ai",
    version="2.0.0",
    author="Finovate Team",
    author_email="info@finovate-audit.com",
    description="Enterprise AI Financial Audit Platform with 22 intelligent agents and 15 ERP connectors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/finovate/audit-nexus-ai",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
        "Typing :: Typed",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.6.0",
            "pre-commit>=3.5.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=2.0.0",
        ],
        "all": [
            "finovate-audit-nexus-ai[dev,docs]",
        ],
    },
    entry_points={
        "console_scripts": [
            "finovate=main:main",
            "finovate-api=main:start_api_server",
            "finovate-desktop=main:start_desktop_app",
        ],
    },
    include_package_data=True,
    package_data={
        "finovate_audit_nexus_ai": [
            "templates/**/*.html",
            "static/**/*",
            "config/**/*.yaml",
            "py.typed",
        ],
    },
)
