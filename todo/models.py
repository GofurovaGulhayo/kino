from __future__ import unicode_literals

import datetime
import os
import textwrap

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse
from django.utils import timezone


def get_attachment_upload_dir(instance, filename):
    """Determine upload dir for task attachment files."""
    return "/".join(["tasks", "attachments", str(instance.task.id), filename])


class TaskList(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(default="")
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Task Lists"

        # Prevents (at the database level) creation of two lists with the same slug in the same group
        unique_together = ("group", "slug")


class Task(models.Model):
    title = models.CharField(max_length=140)
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, null=True)
    created_date = models.DateField(default=timezone.now, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="todo_created_by",
                                   on_delete=models.CASCADE, )
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="todo_assigned_to",
                                    on_delete=models.CASCADE, )
    note = models.TextField(blank=True, null=True)
    priority = models.PositiveIntegerField(blank=True, null=True)

    def overdue_status(self):
        """Returns whether the Tasks's due date has passed or not."""
        if self.due_date:
            if self.completed_date and self.completed_date > self.due_date:
                return True
            elif datetime.date.today() > self.due_date > self.due_date:
                return True

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("todo:task_detail", kwargs={"task_id": self.id})

    def save(self, **kwargs):
        # If Task is being marked complete, set the completed_date
        if self.completed:
            self.completed_date = datetime.datetime.now()
        super(Task, self).save()

    class Meta:
        ordering = ["priority", "created_date"]


class Comments(models.Model):
    """
    Not using Django's built-in comments because we want to be able to save
    a comment and change task details at the same time.
    """

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.datetime.now)

    body = models.TextField(blank=True)

    @property
    def author_text(self):
        if self.author is not None:
            return str(self.author)

    @property
    def snippet(self):
        body_snippet = textwrap.shorten(self.body, width=35, placeholder="...")
        # Define here rather than in __str__ so we can use it in the admin list_display
        return "{author} - {snippet}...".format(author=self.author_text, snippet=body_snippet)

    def __str__(self):
        return self.snippet


class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    file = models.FileField(upload_to=get_attachment_upload_dir, max_length=255)

    def filename(self):
        return os.path.basename(self.file.name)

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    def __str__(self):
        return f"{self.task.id} - {self.file.name}"
