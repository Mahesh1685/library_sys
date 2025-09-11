# librarian/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    total_copies = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class BorrowedBook(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fine = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def calculate_fine(self):
        if self.return_date and self.return_date > self.due_date:
            days = (self.return_date - self.due_date).days
            return days * 1
        elif not self.return_date and timezone.now().date() > self.due_date:
            days = (timezone.now().date() - self.due_date).days
            return days * 1
        return 0

    def save(self, *args, **kwargs):
        if not self.pk:  # New issue
            if self.book.available_copies <= 0:
                raise ValidationError("No copies available.")
            self.book.available_copies -= 1
            self.book.save()
        self.fine = self.calculate_fine()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # On return
        self.book.available_copies += 1
        self.book.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - {self.student.username}"


class BorrowRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} → {self.book.title} ({self.status})"