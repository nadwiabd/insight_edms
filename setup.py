#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import mayan

PACKAGE_NAME = 'insight_edms'
PACKAGE_DIR = 'mayan'

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


def find_packages(directory):
    # Compile the list of packages available, because distutils doesn't have
    # an easy way to do this.
    packages, data_files = [], []
    root_dir = os.path.dirname(__file__)
    if root_dir != '':
        os.chdir(root_dir)

    for dirpath, dirnames, filenames in os.walk(directory):
        if not dirpath.startswith('mayan/media'):
            # Ignore dirnames that start with '.'
            if os.path.basename(dirpath).startswith('.'):
                continue
            if '__init__.py' in filenames:
                packages.append('.'.join(fullsplit(dirpath)))
            elif filenames:
                data_files.append(
                    [dirpath, [os.path.join(dirpath, f) for f in filenames]]
                )

    return packages

install_requires = """
Pillow==4.0.0
PyYAML==3.12
celery==3.1.24
cssmin==0.2.0
Django==1.10.6
django-activity-stream==0.6.3
django-autoadmin==1.1.1
django-celery==3.2.1
django-colorful==1.2
django-compressor==2.1
django-cors-headers==1.2.2
django-downloadview==1.9
django-formtools==2.0
django-pure-pagination==0.3.0
django-model-utils==2.6.1
django-mptt>=0.8.7
django-qsstats-magic==0.7.2
django-rest-swagger==0.3.10
django-stronghold==0.2.8
django-suit==0.2.23
django-widget-tweaks==1.4.1
djangorestframework==3.3.2
djangorestframework-recursive==0.1.1
fusepy==2.0.4
pdfminer==20140328
pycountry==1.20
pyocr==0.4.5
python-dateutil==2.5.3
python-gnupg==0.3.9
python-magic==0.4.13
pytz==2016.7
sh==1.12.11
""".split()

try:
    import pypandoc
    readme = pypandoc.convert_file('README.md', 'rst')
except (IOError, ImportError):
    with open('README.md') as f:
        readme = f.read()

with open('HISTORY.rst') as f:
    history = f.read()

setup(
    author='Insight Media',
    author_email='edms@insightmedia.com.my',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Communications :: File Sharing',
    ],
    description='Free Open Source Electronic Document Management System',
    include_package_data=True,
    install_requires=install_requires,
    license='Apache 2.0',
    long_description=readme + '\n\n' + history,
    name=PACKAGE_NAME,
    packages=find_packages(PACKAGE_DIR),
    platforms=['any'],
    scripts=['mayan/bin/insight-edms.py'],
    url='https://github.com/nadwiabd/insight_edms',
    version=mayan.__version__,
    zip_safe=False,
)
