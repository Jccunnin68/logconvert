from setuptools import setup, find_packages

setup(
    name="logconvert",
    version="1.0.0",
    description="A tool for converting wiki log files to formatted text",
    author="Log Converter Team",
    py_modules=["log_converter", "character_maps"],
    install_requires=[
        "requests",
        "beautifulsoup4",
    ],
    entry_points={
        "console_scripts": [
            "logconvert=log_converter:main",
        ],
    },
    python_requires=">=3.6",
) 