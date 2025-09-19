from django.contrib import admin

from main.models import Block, Course, SubBlock, CourseProfile


class BlockInlineBase(admin.StackedInline):
    extra = 1
    fields = ("title", "content", "order")


class SubBlockInline(BlockInlineBase):
    model = SubBlock


class BlockInline(BlockInlineBase):
    model = Block
    inlines = [SubBlockInline]


class CourseProfileInline(admin.StackedInline):
    model = CourseProfile
    fields = ("cover", "hours_to_complete", "number_of_students")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "created_at", "updated_at")
    search_fields = ("title", "description")
    inlines = [CourseProfileInline, BlockInline]


@admin.register(CourseProfile)
class CourseProfileAdmin(admin.ModelAdmin):
    list_display = ("course", "cover", "hours_to_complete", "number_of_students")
    search_fields = ("cover",)


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filters = ("course",)
    search_fields = ("title", "content")
    inlines = [SubBlockInline]


@admin.register(SubBlock)
class SubBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "block", "order")
    list_filters = ("block__course", "block")
    search_fields = ("title", "content")
