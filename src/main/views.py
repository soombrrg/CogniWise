from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from main.forms import EmailForContactForm
from main.models import Block, Course, SubBlock
from orders.models import Order


def home_view(request):
    return render(request, "main/home.html")


def about_view(request):
    # Just for example
    team_members = [
        {
            "name": "Алексей Петров",
            "position": "Senior Python Developer",
            "bio": "10+ лет опыта",
            "img": "https://images.pexels.com/photos/39866/entrepreneur-startup-start-up-man-39866.jpeg",
        },
        {
            "name": "Мария Иванова",
            "position": "Full-stack Developer",
            "bio": "Специалист по React и Node.js",
            "img": "https://images.pexels.com/photos/8517921/pexels-photo-8517921.jpeg",
        },
        {
            "name": "Дмитрий Смирнов",
            "position": "Data Scientist",
            "bio": "Эксперт в машинном обучении",
            "img": "https://images.pexels.com/photos/845457/pexels-photo-845457.jpeg",
        },
    ]
    return render(request, "main/about.html", {"team_members": team_members})


def course_list_view(request):
    courses = Course.objects.all()
    return render(request, "main/course_list.html", {"courses": courses})


def course_search_view(request):
    query = request.GET.get("query", "")
    courses = Course.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )[:5]
    return render(
        request,
        "main/partials/partial_search_courses.html",
        {"courses": courses},
    )


@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not Order.objects.filter(
        user=request.user, course=course, status="completed"
    ).exists():
        return render(request, "main/access_denied.html", {"course": course})

    first_block = course.blocks.order_by("order").first()
    first_subblock = (
        first_block.subblocks.order_by("order").first() if first_block else None
    )

    return render(
        request,
        "main/course_detail.html",
        {
            "course": course,
            "first_block": first_block,
            "first_subblock": first_subblock,
        },
    )


def load_next_content_view(
    request, course_id, current_block_id, current_subblock_id=None
):
    course = get_object_or_404(Course, id=course_id)
    current_block = get_object_or_404(Block, id=current_block_id, course=course)

    if current_subblock_id:
        current_subblock = get_object_or_404(
            SubBlock, id=current_subblock_id, block=current_block
        )
        next_subblock = (
            SubBlock.objects.filter(
                block=current_block, order__gt=current_subblock.order
            )
            .order_by("order")
            .first()
        )

        if next_subblock:
            return render(
                request,
                "main/partials/partial_content.html",
                {
                    "content": next_subblock,
                    "content_type": "subblock",
                    "next_block_id": current_block.id,
                    "next_subblock_id": next_subblock.id,
                    "course_id": course_id,
                },
            )

        next_block = (
            Block.objects.filter(course=course, order__gt=current_block.order)
            .order_by("order")
            .first()
        )

        if next_block:
            return render(
                request,
                "main/partials/partial_content.html",
                {
                    "content": next_block,
                    "content_type": "block",
                    "next_block_id": next_block.id,
                    "next_subblock_id": None,
                    "course_id": course_id,
                },
            )
    else:
        next_subblock = (
            SubBlock.objects.filter(block=current_block).order_by("order").first()
        )
        if next_subblock:
            return render(
                request,
                "main/partials/partial_content.html",
                {
                    "content": next_subblock,
                    "content_type": "subblock",
                    "next_block_id": current_block.id,
                    "next_subblock_id": next_subblock.id,
                    "course_id": course_id,
                },
            )

        next_block = (
            Block.objects.filter(course=course, order__gt=current_block.order)
            .order_by("order")
            .first()
        )

        if next_block:
            return render(
                request,
                "main/partials/partial_content.html",
                {
                    "content": next_block,
                    "content_type": "block",
                    "next_block_id": next_block.id,
                    "next_subblock_id": None,
                    "course_id": course_id,
                },
            )
    return HttpResponse("")


def load_content_view(request, course_id, block_id, subblock_id=None):
    course = get_object_or_404(Course, id=course_id)
    blocks = course.blocks.order_by("order")

    contents = []
    target_block = get_object_or_404(Block, id=block_id, course=course)
    for block in blocks:
        if block.order <= target_block.order:
            contents.append(
                {
                    "content": block,
                    "content_type": "block",
                    "next_block_id": block.id,
                    "next_subblock_id": None,
                }
            )
            if block.id == block_id and subblock_id:
                subblocks = block.subblocks.order_by("order")
                target_subblock = get_object_or_404(
                    SubBlock, id=subblock_id, block=block
                )
                for subblock in subblocks:
                    if subblock.order <= target_subblock.order:
                        contents.append(
                            {
                                "content": subblock,
                                "content_type": "subblock",
                                "next_block_id": block.id,
                                "next_subblock_id": subblock.id,
                            }
                        )

    return render(
        request,
        "main/partials/partial_content_list.html",
        {
            "contents": contents,
            "target_id": f"{'subblock' if subblock_id else 'block'}-{subblock_id if subblock_id else block_id}",
        },
    )


def modal_open_demo_view(request):
    return render(request, "main/partials/modal_demo.html")


def modal_open_contact_view(request):
    if request.method == "POST":
        form = EmailForContactForm(request.POST)
        if form.is_valid():

            send_email_for_contact(form)
            return render(request, "main/partials/modal_successful_sending.html")
    else:
        form = EmailForContactForm()
    return render(request, "main/partials/modal_contact.html", {"form": form})


def modal_close_view(request):
    return HttpResponse('<div id="modal"></div>')


def send_email_for_contact(form):
    subject = "Пользователь хочет связаться"

    context = {
        "name": form.cleaned_data["name"],
        "email": form.cleaned_data["email"],
        "phone": form.cleaned_data["phone"],
        "tg_username": form.cleaned_data["tg_username"],
    }

    message = render_to_string("main/email_for_contact.html", context)

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],
        html_message=message,
    )
