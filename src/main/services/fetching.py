from typing import Literal, Union

from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404

from main.models import Block, Course, SubBlock


def get_courses_list():
    courses = (
        Course.objects.all()
        .select_related("course_profile")
        .defer(
            "created_at",
            "updated_at",
        )
    )
    return courses


def get_courses_by_query(query: str):
    courses = (
        Course.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        .select_related("course_profile")
        .defer(
            "created_at",
            "updated_at",
        )
    )
    return courses


def get_course_first_content(course_id):
    prefetch_subblock = Prefetch(
        "subblocks",
        queryset=SubBlock.objects.order_by("order"),
    )
    prefetch_block = Prefetch(
        "blocks",
        queryset=Block.objects.prefetch_related(prefetch_subblock).order_by("order"),
    )
    course = get_object_or_404(
        Course.objects.prefetch_related(prefetch_block).only("title", "description"),
        id=course_id,
    )

    first_block = course.blocks.first()
    first_subblock = first_block.subblocks.first()
    first_content = {
        "course": course,
        "first_block": first_block,
        "first_subblock": first_subblock,
    }
    return first_content


def get_block(block_id: int, only_fields=None) -> Block:
    only_fields = only_fields or []
    block = get_object_or_404(Block.objects.only(*only_fields), id=block_id)
    return block


def get_next_block(current_block, course_id: int) -> Block:
    next_block = (
        Block.objects.filter(course__id=course_id, order__gt=current_block.order)
        .order_by("order")
        .first()
    )
    return next_block


def get_next_subblock(block: Block, current_subblock_id=None) -> SubBlock:
    if current_subblock_id:
        current_subblock = get_object_or_404(
            SubBlock.objects.only("order"), id=current_subblock_id, block__id=block.id
        )
        next_subblock = (
            SubBlock.objects.filter(block=block.id, order__gt=current_subblock.order)
            .order_by("order")
            .first()
        )
    else:
        next_subblock = (
            SubBlock.objects.filter(block__id=block.id).order_by("order").first()
        )
    return next_subblock


def build_next_content(
    content: Union[Block, SubBlock],
    content_type: Union[Literal["block"], Literal["subblock"]],
    course_id: int,
    block_id: int,
):
    subblock_id = content.id if content_type == "subblock" else None
    next_content = {
        "content": content,
        "content_type": content_type,
        "next_block_id": block_id,
        "next_subblock_id": subblock_id,
        "course_id": course_id,
    }
    return next_content


def get_example_team_members():
    # Example members, change if needed
    members = [
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
    return members
