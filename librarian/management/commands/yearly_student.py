from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import CustomUser
from librarian.models import BorrowedBook
from datetime import date

class Command(BaseCommand):
    help = 'Promote students yearly. Delete only 3rd-year students with zero fines.'

    def handle(self, *args, **options):
        today = date.today()
        # Run only on June 30
        if today.month != 6 or today.day != 30:
            self.stdout.write(self.style.WARNING("Not June 30 — skipping."))
            return

        self.stdout.write("Starting yearly student update...")

        promoted = 0
        deleted = 0

        # Step 1: Delete ONLY 3rd-year students with NO pending fines
        third_year_students = CustomUser.objects.filter(
            role='student',
            year_of_study=3
        )

        for student in third_year_students:
            # Check if student has any unpaid fines
            has_fine = BorrowedBook.objects.filter(
                student=student,
                fine__gt=0
            ).exists()

            if not has_fine:
                student.delete()
                deleted += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"Skipped deletion: {student.email} has pending fines.")
                )

        # Step 2: Promote 2nd → 3rd year
        second_to_third = CustomUser.objects.filter(
            role='student',
            year_of_study=2
        )
        for student in second_to_third:
            student.year_of_study = 3
            student.save()
            promoted += 1

        # Step 3: Promote 1st → 2nd year
        first_to_second = CustomUser.objects.filter(
            role='student',
            year_of_study=1
        )
        for student in first_to_second:
            student.year_of_study = 2
            student.save()
            promoted += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Yearly update complete: {promoted} promoted, {deleted} deleted."
            )
        )