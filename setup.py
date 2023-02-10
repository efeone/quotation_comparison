from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in quotation_comparison/__init__.py
from quotation_comparison import __version__ as version

setup(
	name="quotation_comparison",
	version=version,
	description="Quotation Comparison Tool for ERPNext",
	author="efeone",
	author_email="info@efeone.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
