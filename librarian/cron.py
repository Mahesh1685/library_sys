from datetime import timedelta, datetime
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from librarian.models import BorrowedBook
from librarian.reports import (generate_monthly_report_pdf)
from django.core.mail import EmailMessage
from users.models import CustomUser


def send_due_date_reminders():
    upcoming_date = timezone.now().date() + timedelta(days=7)
    books = BorrowedBook.objects.filter(handover_date__isnull=False, due_date=upcoming_date, return_date__isnull=True)
    for b in books:
        send_mail(
            "📚 Reminder: Book Due Soon",
            f"""
        Hello {b.student.username},

        This is a reminder that the book "{b.book.title}" is due on {b.due_date}.
        Please return it on time to avoid fines (₹5/day).

        Thank you!
        Library Management System
                    """,
            settings.DEFAULT_FROM_EMAIL,
            [b.student.email]
        )

def send_monthly_report():
    from .reports import generate_monthly_report_pdf
    pdf_path = generate_monthly_report_pdf()
    librarian = CustomUser.objects.filter(role='librarian', is_approved=True).first()
    if librarian:
        msg = EmailMessage(
            f"📊 Monthly Library Report - {(timezone.now().replace(day=1) - timedelta(days=1)).strftime('%B %Y')}",
            "See attached report.",
            settings.DEFAULT_FROM_EMAIL,
            [librarian.email]
        )
        msg.attach_file(pdf_path)
        msg.send()