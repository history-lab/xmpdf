from setuptools import setup

setup(name="xmpdf",
      version="0.3",
      description="A Python package for extracting email metadata and text from \
a PDF file",
      author="Ben Lis",
      url="https://github.com/history-lab/xmpdf",
      license="MIT License",
      install_requires=["pdftotext", "python-magic", "jsonpickle"],
      py_modules=["pgparse", "xmpdf"])
