from django.contrib.auth.tokens import default_token_generator


def is_verified_by_token(user, token) -> bool:
    return user is not None and default_token_generator.check_token(user, token)
