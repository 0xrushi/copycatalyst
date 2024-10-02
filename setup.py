from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="copycatalyst",
    version="0.1.0",
    author="0xrushi",
    author_email="",
    description="A file selection and content copying tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0xrushi/copycatalyst",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "prompt_toolkit>=3.0.0",
        "pyperclip>=1.8.0",
    ],
    entry_points={
        "console_scripts": [
            "copycatalyst=copycatalyst.cli:main",
        ],
    },
)