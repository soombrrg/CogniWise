from django.urls import path

from main.views import (
    about_view,
    course_detail_view,
    course_list_view,
    home_view,
    load_content_view,
    load_next_content_view,
    modal_close_view,
    modal_open_contact_view,
    modal_open_demo_view,
    course_search_view,
)

app_name = "main"

urlpatterns = [
    path("", home_view, name="home"),
    path("about/", about_view, name="about"),
    path("modal-open-demo/", modal_open_demo_view, name="modal-open-demo"),
    path("modal-open-contact/", modal_open_contact_view, name="modal-open-contact"),
    path("modal-close/", modal_close_view, name="modal-close"),
    path("courses/", course_list_view, name="courses-list"),
    path("course-search/", course_search_view, name="course-search"),
    path("courses/<int:course_id>/", course_detail_view, name="course-detail"),
    path(
        "courses/<int:course_id>/load-next/<int:current_block_id>/",
        load_next_content_view,
        name="load-next-content",
    ),
    path(
        "courses/<int:course_id>/load-next/<int:current_block_id>/<int:current_subblock_id>/",
        load_next_content_view,
        name="load-next-content-with-subblock",
    ),
    path(
        "courses/<int:course_id>/load/<int:block_id>/",
        load_content_view,
        name="load-content",
    ),
    path(
        "courses/<int:course_id>/load/<int:block_id>/<int:subblock_id>/",
        load_content_view,
        name="load-content-with-subblock",
    ),
]
