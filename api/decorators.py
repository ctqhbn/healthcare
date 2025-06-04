from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'admin':
            return HttpResponseForbidden("Bạn không có quyền truy cập")
        return view_func(request, *args, **kwargs)
    return wrapper
