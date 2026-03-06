from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jep-sdk-py",
    version="0.1.0",
    description="Complete Python SDK for JEP Protocol - Judgment, Delegation, Termination, Verification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="JEP Foundation Ltd.",
    author_email="signal@humanjudgment.org",
    url="https://github.com/jep-protocol/sdk-py",
    project_urls={
        "Bug Tracker": "https://github.com/jep-protocol/sdk-py/issues",
        "Documentation": "https://github.com/jep-protocol/sdk-py#readme",
        "Source Code": "https://github.com/jep-protocol/sdk-py",
    },
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
    ],
    keywords="jep, protocol, judgment, delegation, termination, verification, ietf, draft, ai, accountability, traceability",
    license="MIT",
)
