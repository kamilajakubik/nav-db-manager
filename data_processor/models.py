from django.db import models

from navigation.models import DataCycle


class ArincFile(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    processing_errors = models.TextField(blank=True, null=True)
    cycle = models.ForeignKey(
        DataCycle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="files",
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.file.name} - {self.status} - cycle {self.cycle}"
