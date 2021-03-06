import os
from setuptools import setup

REPODIR = os.path.dirname(os.path.realpath(__file__))

def _get_longdesc(repodir):
    return open(os.path.join(repodir, 'README.rst')).read()


def _get_license(repodir):
    return open(os.path.join(repodir, 'LICENSE.txt')).read()


def _get_version(repodir):
    version = 'UNKNOWN'
    init = open(os.path.join(repodir, 'pypfop', '__init__.py'))
    for line in init.readlines():
        if '__version__' in line and '=' in line:
            version = line.split('=')[-1].strip()
            version = version.replace('"', '').replace("'", '')
            break
    init.close()
    return version


description = 'Document preprocessor for Apache FOP.'
version = _get_version(REPODIR)
longdesc = _get_longdesc(REPODIR)
license_ = _get_license(REPODIR)
classifiers = ['Development Status :: 3 - Alpha',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: Apache Software License',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 2.6',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Office/Business',
               'Topic :: Software Development :: Libraries',
               'Topic :: Text Processing :: Filters']
requires = ['Mako',
            'cssutils',
            'cssselect',
            'lxml']
setup(name='pypfop',
      version=version,
      author='Joel Rivera',
      author_email='rivera@joel.mx',
      maintainer='Joel Rivera',
      maintainer_email='rivera@joel.mx',
      url='https://github.com/cyraxjoe/pypfop',
      license=license_,
      provides=['pypfop',],
      packages=['pypfop',
                'pypfop.templates'],
      classifiers=classifiers,
      install_requires=requires,
      include_package_data=True,
      platforms=['linux2', 'win32', 'cygwin', 'darwin'],
      description=description,
      long_description=longdesc)
