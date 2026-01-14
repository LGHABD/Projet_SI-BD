from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def role_required(*roles):
    def deco(view_func):
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                return HttpResponseForbidden("Accès refusé.")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return deco
