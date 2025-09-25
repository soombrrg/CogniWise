from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from main.decorators import purchase_required
from main.forms import EmailForContactForm
from main.services.fetching import (
    build_next_content,
    get_block,
    get_course_first_content,
    get_courses_by_query,
    get_courses_list,
    get_example_team_members,
    get_next_block,
    get_next_subblock,
)
from main.services.mailing import send_email_for_contact


def home_view(request):
    return render(request, "main/home.html")


def about_view(request):
    team_members = get_example_team_members()
    return render(request, "main/about.html", {"team_members": team_members})


def course_list_view(request):
    """Return all courses"""
    courses = get_courses_list()
    return render(request, "main/course_list.html", {"courses": courses})


def courses_search_view(request):
    """Return searched courses"""
    query = request.GET.get("query", "")
    courses = get_courses_by_query(query)
    return render(
        request,
        "main/partials/partial_search_courses.html",
        {"courses": courses},
    )


@login_required
@purchase_required
def course_detail_view(request, course_id: int):
    """Return first part of course"""

    first_content = get_course_first_content(course_id)
    return render(
        request,
        "main/course_detail.html",
        first_content,
    )


@login_required
@purchase_required
def load_next_content_view(
    request, course_id: int, current_block_id: int, current_subblock_id=None
):
    """Return next part of course"""
    current_block = get_block(current_block_id, only_fields=["order"])

    # Return next subblock if exist
    next_subblock = get_next_subblock(current_block, current_subblock_id)
    if next_subblock:
        next_content = build_next_content(
            next_subblock, "subblock", course_id, current_block_id
        )
        return render(
            request,
            "main/partials/partial_content.html",
            next_content,
        )

    # Return next block if exist
    next_block = get_next_block(current_block, course_id)
    if next_block:
        next_content = build_next_content(next_block, "block", course_id, next_block.id)
        return render(
            request,
            "main/partials/partial_content.html",
            next_content,
        )
    return HttpResponse("")


def modal_open_demo_view(request):
    demo_url = "https://www.youtube.com/embed/u_sIfs7Yom4"
    return render(request, "main/partials/modal_demo.html", {"demo_url": demo_url})


def modal_open_contact_view(request):
    if request.method == "POST":
        form = EmailForContactForm(request.POST)
        if form.is_valid():
            send_email_for_contact(form.cleaned_data)
            return render(request, "main/partials/modal_successful_sending.html")
    else:
        form = EmailForContactForm()
    return render(request, "main/partials/modal_contact.html", {"form": form})


def modal_close_view(request):
    return HttpResponse('<div id="modal"></div>')
