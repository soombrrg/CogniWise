from django.core.cache import cache

from orders.models import Order


def is_purchased(user, course_id) -> bool:
    """Check if course is purchased or not, using cache"""
    cache_key = f"purchase_status_{user.id}_{course_id}"
    purchase_status = cache.get(cache_key)

    # if not in cache
    if purchase_status is None:
        purchase_status = Order.objects.filter(
            user=user, course__id=course_id, status="completed"
        ).exists()
        cache.set(cache_key, purchase_status, 1800)
    return purchase_status


def create_order(user, course, price, status) -> Order:
    order = Order.objects.create(
        user=user,
        course=course,
        total_price=price,
        status=status,
    )
    return order
