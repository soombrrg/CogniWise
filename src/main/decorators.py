from functools import wraps

from django.shortcuts import get_object_or_404, render

from main.models import Course
from orders.services import is_purchased


def purchase_required(view_func):
    """Decorator. For purchase status checking, with caching"""

    @wraps(view_func)
    def wrapper(request, course_id, *args, **kwargs):
        purchase_status = is_purchased(request.user, course_id)

        if not purchase_status:
            course = get_object_or_404(Course, id=course_id)
            return render(request, "main/access_denied.html", {"course": course})

        return view_func(request, course_id, *args, **kwargs)

    return wrapper
