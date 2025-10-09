#This file is used to promote students year wise from 1st to 2nd year & 2nd to 3rd year & 3rd year to remove the data from library database


from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import CustomUser
from datetime import date


class Command(BaseCommand):
    help='Promote students to next year and delete final year'
    def handle(self, *args, **options):
        today = date.today()
        if today.month!=6 and today.day!=30: #30th of june promotes and deletes the student record
            self.stdout.write('Not today')
            return
        self.stdout.write('Starting our progress')
        promoted=0
        deleted=0
        graduates=CustomUser.objects.filter(role='student',year_of_study=3) #deletes third year data
        deleted=graduates.count()
        graduates.delete()
        second_to_third=CustomUser.objects.filter(role='student',year_of_study=2) #promotes to 3rd year
        for student in second_to_third:
            student.year_of_study=3
            student.save()
            promoted+=1
        first_to_second=CustomUser.objects.filter(role='student',year_of_study=1) #promotes to 2nd year
        for student in first_to_second:
            student.year_of_study=2
            student.save()
            promoted+=1
        self.stdout.write(self.style.SUCCESS('promoted:{promoted} deleted:{deleted}'))