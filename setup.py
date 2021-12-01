from setuptools import setup

setup(name="xmpdf",
      version="0.1",
      description="A Python module for extracting email metadata and text from \
a PDF file",
      author="Ben Lis",
      url="https://github.com/history-lab/xmpdf",
      license="Apache License",
      install_requires=["pdftotext", "python-magic"],
      py_modules=["pgparse", "xmpdf"])
