# coding=utf-8
from setuptools import find_packages
from setuptools import setup

version = '0.7.dev0'

setup(
    name='collective.garbagecan',
    version=version,
    description=(
        "Provides a garbage can for managing deleted objects."
    ),
    long_description="%s\n" % (
        open("README.rst").read(),
    ),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 5.2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 5 - Production/Stable',

    ],
    keywords='Plone undelete garbage trash can',
    author='enfold',
    author_email='info@enfoldsystems.com',
    url='http://svn.plone.org/svn/collective/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.CMFCore',
        'zope.globalrequest',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
        ]
    },
    entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone

      [console_scripts]
      expunge = collective.garbagecan.scripts.expunge:main
      """
)
