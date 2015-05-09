#!/usr/bin/env python

from setuptools import find_packages, setup

from przelewy24 import VERSION

setup(
  name = 'django_oscar_przelewy24',
  version = VERSION,
  description = 'Przelewy24.pl payment gateway for django-oscar e-commerce',
  long_description=open('README.md').read(),
  author = 'Lukasz Prusiel',
  author_email = 'kisiel85@go2.pl',
  url = 'https://github.com/kisiel/django-oscar-przelewy24',
  license='BSD License',
  platforms=['OS Independent'],
  packages=find_packages(exclude=['sandbox*', 'tests*']),
  include_package_data=True,
  keywords = ['django', 'oscar', 'przelewy24.pl', 'e-commerce'],
  classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ],
  install_requires=[
      'Django>=1.6',
      'django-oscar>=1.0.2',
      'pycountry>=1.10',
      'requests>=2.5.1'
  ],
)