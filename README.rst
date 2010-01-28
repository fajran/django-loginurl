================
Django Login URL
================

This is a simple application for Django that allows an anonymous visitor to
log in as a user by only visiting a URL. 

By default, the URL is only valid once and cannot be used multiple times.
Other schemes that involve the number of visit and/or an expiry date can
also be created. For example, it is possible to create a log in URL that
only valid for 5 visits before next week using this application.


Configuration
-------------

1. Add django-loginurl application into your Django project. Modify your
   ``settings.py`` like the following::

        INSTALLED_APPS = (
            ...
            'loginurl',
            ...
        )

2. Add the authentication backend of this django-loginurl application to
   your project's ``settings.py``.
   ::

        AUTHENTICATION_BACKENDS = (
            'django.contrib.auth.backends.ModelBackend',
            'loginurl.backends.LoginUrlBackend',
        )
   
   The first authentication backend is the default and if your project uses
   the Django's standard authentication mechanism, you will need that.

   Consult the Django documentation for more information regarding the
   backend. See
   http://docs.djangoproject.com/en/dev/topics/auth/#other-authentication-sources


3. Include the application's ``urls.py`` to your project.
   ::

        urlpatterns = patterns('',
            ...
            (r'^loginurl/', include('loginurl.urls')),
            ...
        )
    
   This will make requests to ``loginurl/`` are handled by django-loginurl.
   If the configuration is put inside the project's ``urls.py``, the log in
   URL will look like the following::

       http://example.com/loginurl/a-secret-key


Scheduled Task
--------------

To keep your database clean from expired secret keys, a scheduled task need
to be set up. This task should do one of the following.

1. Call ``loginurl_cleanup`` command from the Django's management script, or

2. Open a special URL that will trigger the clean up, ``loginurl/cleanup/``.
   e.g. http://example.com/loginurl/cleanup/

You can use crontab or the web based one to set this up. A daily or weekly
task should be enough.


Usage
-----

If your application need to create a one time log in URL, what you need to
do is calling ``loginurl.utils.create`` with a user object as the parameter.
The resulting object is an instance of ``loginurl.models.Key`` that has a
property called ``key`` that contains a unique key for the log in URL.
::

    import loginurl.utils

    def create_login_url(user):
        key = loginurl.utils.create(user)
        url = 'http://example.com/loginurl/%s' % key.key

        return url

