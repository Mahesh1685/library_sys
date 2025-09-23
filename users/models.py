# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('librarian', 'Librarian'),
    ]
    YEAR_CHOICES = [
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
    ]
    DEPARTMENT_CHOICES = [
        ('B.Sc.C.S.', 'B.Sc.Computer Science'),
        ('B.C.A.', 'B.Computer Application'),
        ('B.Com.', 'B.Commerce'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_approved = models.BooleanField(default=False)
    pending_approval = models.BooleanField(default=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    year_of_study = models.IntegerField(choices=YEAR_CHOICES, null=True, blank=True)  # Only for students
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES,default='B.Com.')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','role']

