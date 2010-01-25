from distutils.core import setup

import onetime

setup(name='django-onetime',
      version=onetime.__version__,
      description='A one time authentication application.',
      author='Fajran Iman Rusadi',
      author_email='fajran@gmail.com',
      url='http://github.com/fajran/django-onetime/',
      download_url='http://github.com/fajran/django-onetime/tarball/v0.1.0',
      packages=['onetime'],
      package_dir={'onetime': 'onetime'},
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      )
