import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='ifb-wrapper',
      version='1.5.1',
      description='iFormBuilder API Wrapper',
      long_description=README,
      long_description_content_type="text/markdown",
      url='https://github.com/jhsu98/ifb-wrapper',
      author='Jonathan Hsu',
      author_email='jhsu@zerionsoftware.com',
      license='MIT',
      python_requires='>=3.0',
      packages=['ifb'],
      install_requires=[
            'pyjwt',
            'requests'
      ],
      zip_safe=False)