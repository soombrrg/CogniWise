from typing import Optional

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_resized import ResizedImageField


class Course(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название курса")
    description = models.TextField(
        blank=True, verbose_name="Описание курса", max_length=250
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=129.90, verbose_name="Стоимость (RUB)"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        if created:
            try:
                self.course_profile
            except CourseProfile.DoesNotExist:
                CourseProfile.objects.create(course=self)


class CourseProfile(models.Model):
    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name="course_profile",
        verbose_name="Профиль курса",
    )
    hours_to_complete = models.PositiveSmallIntegerField(
        default=1,
        validators=[MaxValueValidator(200), MinValueValidator(1)],
        verbose_name="Часов на выполнение",
    )
    number_of_students = models.PositiveIntegerField(
        default=0, verbose_name="Кол-во учеников"
    )
    cover = ResizedImageField(
        size=[854, 480],
        crop=["middle", "center"],
        upload_to="covers/",
        default="covers/default_cover.jpeg",
        verbose_name="Обложка курса",
    )

    class Meta:
        verbose_name = "Профиль курса"
        verbose_name_plural = "Профили курсов"
        ordering = ["-number_of_students"]

    def __str__(self):
        return f"Профиль для курса: {self.course.title}"


class BlockBaseManager(models.Manager):
    def get_max_order(self, filter_fields: Optional[dict] = None):
        filter_fields = filter_fields or {}

        result = self.only("order").filter(**filter_fields).order_by("order").last()
        max_order = result.order
        return max_order

    def do_reordering(self, filter_fields: Optional[dict] = None):
        filter_fields = filter_fields or {}

        course_subblocks = list(
            self.only("order").filter(**filter_fields).order_by("order")
        )
        for index, subblock in enumerate(course_subblocks, 1):
            if subblock.order != index:
                subblock.order = index
        self.bulk_update(course_subblocks, ["order"])


class Block(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="blocks", verbose_name="Курс"
    )
    title = models.CharField(max_length=200, verbose_name="Название блока")
    content = models.TextField(verbose_name="Содержимое блока")
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
    )

    objects = BlockBaseManager()

    class Meta:
        verbose_name = "Блок"
        verbose_name_plural = "Блоки"
        ordering = ["course", "order"]
        unique_together = ("course", "order")

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def save(self, *args, **kwargs):
        if self.pk is None and self.order is None:
            max_order = Block.objects.get_max_order({"course": self.course})
            self.order = max_order + 1

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        course = self.course
        # For order resetting
        super().delete(*args, **kwargs)

        Block.objects.do_reordering({"course": course})


class SubBlock(models.Model):
    block = models.ForeignKey(
        Block, on_delete=models.CASCADE, related_name="subblocks", verbose_name="Блок"
    )
    title = models.CharField(max_length=200, verbose_name="Название подблока")
    content = models.TextField(verbose_name="Содержимое подблока")
    order = models.PositiveIntegerField(blank=True, verbose_name="Порядок")

    objects = BlockBaseManager()

    class Meta:
        verbose_name = "Подблок"
        verbose_name_plural = "Подблоки"
        ordering = ["block", "order"]
        unique_together = ("block", "order")

    def __str__(self):
        return f"{self.block.title} - {self.title}"

    def save(self, *args, **kwargs):
        if self.pk is None and self.order is None:
            max_order = SubBlock.objects.get_max_order({"block": self.block})
            self.order = max_order + 1

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        block = self.block
        # For order resetting
        super().delete(*args, **kwargs)

        SubBlock.objects.do_reordering({"block": block})
