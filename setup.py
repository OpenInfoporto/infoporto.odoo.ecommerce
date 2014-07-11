from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='infoporto.odoo.ecommerce',
      version=version,
      description="Odoo ecommerce functionalities",
      long_description="",
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='odoo ecommerce',
      author='Andrea Carmisciano',
      author_email='andrea.carmisciano@infoporto.it',
      url='http://www.infoporto.it',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['infoporto', 'infoporto.odoo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity [grok]',
          'plone.namedfile [blobs]',
          # -*- Extra requirements: -*-
          'money',
          'paypalrestsdk'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      # The next two lines may be deleted after you no longer need
      # addcontent support from paster and before you distribute
      # your package.
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],

      )
