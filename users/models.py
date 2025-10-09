from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser): #defines what details user db must have
    ROLE_CHOICES = [ #roles for our project
        ('student', 'Student'),
        ('librarian', 'Librarian'),
    ]
    YEAR_CHOICES = [ #year for graduation and question paper allotment
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
    ]
    DEPARTMENT_CHOICES = [ #for question paper allotment
        ('B.Sc.C.S.', 'B.Sc.Computer Science'),
        ('B.C.A.', 'B.Computer Application'),
        ('B.Com.', 'B.Commerce'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_approved = models.BooleanField(default=False) #shows whether user is approved or not
    pending_approval = models.BooleanField(default=True) #shows the no of users with pending approval
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    year_of_study = models.IntegerField(choices=YEAR_CHOICES, null=True, blank=True)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES,default='B.Com.')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','role']

