# Lightweight Django Blog

This is a lightweight blogging tool with create, edit and delete functionality for articles, configured for use on App Engine using [Djangae](https://github.com/potatolondon/djangae).

[Lightweight Django Blog](https://lightweight-django-blog.appspot.com/) uses [Clean Blog](http://startbootstrap.com/template-overviews/clean-blog/), a stylish, responsive blog theme for [Bootstrap](http://getbootstrap.com/) and [SB Admin 2](http://startbootstrap.com/template-overviews/sb-admin-2/), an admin dashboard template.

## Features

* Translatable project
* User Roles
* SEO friendly urls
* Complete admin interface

## Get started
In the `lightweight-django-blog` directory, run:

    ./install_deps
    python manage.py collectstatic
    python manage.py test
    python manage.py runserver

## Deployment
Create a Google App Engine project. Edit `app.yaml` and change `application: lightweight-django-blog` to `application: your-app-id` and edit `settings.py` changing `DEBUG = True` to `DEBUG = False`.

Then, if you're in the `lightweight-django-blog` directory, run:

    $ appcfg.py update ./

If you have two-factor authentication enabled in your Google account, run:

    $ appcfg.py --oauth2 update ./



## User Roles

User roles determine the access level or permissions of a person authorized (invited by an Administrator) to use Lightweight Django Blog.

**Summary**

* Administrator – nothing is off limits
* Editor – has access to all articles.
* Author – can write, edit, and publish their own articles.
* Contributor – has no publishing capability, but can write and edit their own articles until they are published.
* Follower – has no privileges (his google id and email is saved)


Each user role is capable of everything that a less powerful role is capable of. (In others words, Editors can do everything Authors can do, Authors can do everything Contributors can do, and so on.)

**Administrator**

An Administrator has full power over the site and can do absolutely everything. Administrators can create more Administrators, invite new users,  remove users, and change user roles. They have complete control over articles and other users.

**Editor**

An Editor can create, edit, publish, and delete any article (not just their own).

**Author**

An Author can create, edit, publish, and delete only their own articles.

**Contributor**

A Contributor can create and edit only their own articles, but cannot publish them.

**Follower**

A Follower cannot do anything.
