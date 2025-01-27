from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pybcm",
    version="0.1.13",
    description="Themis is a concept modeling tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="",
    author_email="",
    url="https://github.com/ThomasRohde/themis",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "bcm": [
            "static/*",
            "templates/*",
            "*.ico",
            "*.html",
            "*.md"
        ]
    },
    install_requires=[
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "jinja2>=3.1.5",
        "python-pptx>=1.0.2",
        "markdown>=3.7",
        "fastapi>=0.115.6",
        "uvicorn[standard]>=0.34.0",
        "openpyxl>=3.1.5",
        "pandas>=2.2.3"
    ],
    entry_points={
        "console_scripts": [
            "themis=bcm.api.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
)
