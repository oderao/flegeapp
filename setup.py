from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in flegeapp/__init__.py
from flegeapp import __version__ as version

setup(
	name="flegeapp",
	version=version,
	description="Healthcare App",
	author="Flege",
	author_email="flege@flege.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
