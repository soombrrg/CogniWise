from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from main.models import CourseProfile
from orders.models import Order
from users.models import CustomUser, CustomUserProfile


def get_user_by_uidb64(uidb64) -> CustomUser:
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    return user


def get_profile_by_user(user) -> CustomUserProfile:
    try:
        profile = user.profile
    except CustomUserProfile.DoesNotExist:
        profile = CustomUserProfile(user=user)
    return profile


def get_user_profile_data(user):

    user_orders = (
        Order.objects.filter(user=user)
        .select_related("course")
        .only("created_at", "total_price", "status", "course__title")
        .all()
    )

    completed_course = [
        order.course for order in user_orders if order.status == "completed"
    ]

    courses_cover = (
        CourseProfile.objects.filter(course__in=completed_course)
        .select_related("course")
        .only("cover", "course__title")
        .order_by()
    )

    user_profile_data = {
        "user_orders": user_orders,
        "courses_cover": courses_cover,
    }
    return user_profile_data
