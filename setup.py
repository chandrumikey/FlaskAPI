from setuptools import setup, find_packages
import os

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="flashapi",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An ultra-fast, modern web framework for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/flashapi",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/flashapi/issues",
        "Documentation": "https://github.com/yourusername/flashapi/wiki",
        "Source Code": "https://github.com/yourusername/flashapi",
    },
    packages=find_packages(include=["flashapi", "flashapi.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "uvicorn[standard]>=0.20.0",
            "httpx>=0.24.0",
        ],
        "redis": ["redis>=4.5.0"],
        "full": [
            "uvicorn[standard]>=0.20.0",
            "redis>=4.5.0",
            "gunicorn>=20.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "flashapi=flashapi.cli:main",
        ],
    },
    keywords=["web", "framework", "api", "asgi", "fast", "async"],
    include_package_data=True,
)