from setuptools import find_packages, setup

META_VERSION = "1.0"
VERSION = "0.0.02b8"
DESCRIPTION = "Python SDK for AMDAPi API"

with open("README.md", "r", encoding="utf-8") as file:
    LONG_DESCRIPTION = file.read()


with open("requirements.txt", encoding="utf-8") as f:
    content = f.readlines()
requirements = [x.strip() for x in content if "git+" not in x]

setup(
    name="amdapi",
    version=VERSION,
    url="https://github.com/AMDA-pi/amda-pi-python-sdk",
    download_url="https://github.com/AMDA-pi/amda-pi-python-sdk",
    project_urls={
        "AMDAPi": "https://www.amdapi.com/",
    },
    author="Omer Eltayeb",
    author_email="Omer.Eltayeb@amdapi.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    packages=find_packages(),
    keywords=["python", "amdapi", "AMDA", "PI", "amdapi-sdk"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Customer Service",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
