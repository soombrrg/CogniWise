from django.core.cache import cache

from users.models import CustomUserProfile


def user_avatar(request):
    """Get user avatar URL with caching"""
    if not request.user.is_authenticated:
        return {"avatar_url": None}

    cache_key = f"user_avatar_url_{request.user.id}"
    avatar_url = cache.get(cache_key, None)

    if avatar_url:
        return {"avatar_url": avatar_url}

    try:
        profile = CustomUserProfile.objects.only("avatar").get(user=request.user)
        avatar_url = profile.avatar.url if profile.avatar else None
    except CustomUserProfile.DoesNotExist:
        avatar_url = None

    cache.set(cache_key, avatar_url, 1800)

    return {"avatar_url": avatar_url}
