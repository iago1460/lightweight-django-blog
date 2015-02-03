from functools import wraps

from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from blog.utils import has_enough_privileges
from google.appengine.api import users


def login_required(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(users.create_login_url(dest_url=request.GET.get('next')))
        return function(request, *args, **kwargs)

    return decorator


def has_permission_level(group_name):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not has_enough_privileges(request.user.role, group_name):
                return redirect('dashboard:index')
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
