#Used to store a schema in our database

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import CustomUser

User = get_user_model()

class Book(models.Model): #schema for books
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    total_copies = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class BorrowedBook(models.Model): #schema for Borrowed Books in library
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True) #when the librarian approve the borrow request
    due_date = models.DateField()
    handover_date=models.DateField(null=True, blank=True) #when the student physically borrowed his book from librarian
    return_date = models.DateField(null=True, blank=True) #when the student returned his book
    fine = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def calculate_fine(self): #function for calculating fiine
        if self.return_date and self.return_date > self.due_date:
            days = (self.return_date - self.due_date).days
            return days * 1
        elif not self.return_date and timezone.now().date() > self.due_date:
            days = (timezone.now().date() - self.due_date).days
            return days * 1
        return 0

    def save(self, *args, **kwargs): #function for saving the book details
        if not self.pk:  # New issue
            if self.book.available_copies <= 0:
                raise ValidationError("No copies available.")
            self.book.available_copies -= 1
            self.book.save()
        self.fine = self.calculate_fine()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs): #function for deleting a book
        # On return
        self.book.available_copies += 1
        self.book.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - {self.student.username}"


class BorrowRequest(models.Model): #schema for handling borrow request details
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

# using department choices for distinguish qn papers based on department
DEPARTMENT_CHOICES = [
        ('B.Sc.C.S.','B.Sc.Computer Science'),
        ('B.C.A.','B.Computer Application'),
        ('B.Com.','B.Commerce'),
    ]

class QuestionPaper(models.Model): #schema for handling qn papers details based on semester wise
    SUBJECT_CHOICES = [
        ('Python','Python Programming'),
        ('Java','Java Programming'),
        ('Integration','Integral Calculus'),
        ('Banking','Intro to Banking'),
    ]
    SEMESTER_CHOICES = [
        ('sem1','Semester1'),
        ('sem2', 'Semester2'),
        ('sem3', 'Semester3'),
        ('sem4', 'Semester4'),
        ('sem5', 'Semester5'),
        ('sem6', 'Semester6'),
    ]
    subject=models.CharField(max_length=30, choices=SUBJECT_CHOICES)
    semester=models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    department=models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    pdf=models.FileField(upload_to='qns/')
    uploaded_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_subject_display()} - {self.get_department_display()} {self.semester}"