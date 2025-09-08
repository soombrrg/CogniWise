from django.urls import path

from main.views import (
    home_view,
    about_view,
    reviews_view,
    pricing_view,
    course_list_view,
    course_detail_view,
    load_next_content,
    load_content,
)

app_name = "main"

urlpatterns = [
    path("", home_view, name="home"),
    path("about/", about_view, name="about"),
    path("reviews/", reviews_view, name="reviews"),
    path("pricing/", pricing_view, name="pricing"),
    path("courses/", course_list_view, name="courses_list"),
    path("courses/<int:course_id>/", course_detail_view, name="course_detail"),
    path(
        "courses/<int:course_id>/load-next/<int:current_block_id>/",
        load_next_content,
        name="load_next_content",
    ),
    path(
        "courses/<int:course_id>/load-next/<int:current_block_id>/<int:current_subblock_id>/",
        load_next_content,
        name="load_next_content_with_subblock",
    ),
    path(
        "courses/<int:course_id>/load/<int:block_id>/",
        load_content,
        name="load_content",
    ),
    path(
        "courses/<int:course_id>/load/<int:block_id>/<int:subblock_id>/",
        load_content,
        name="load_content_with_subblock",
    ),
]
