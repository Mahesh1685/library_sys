from datetime import timedelta, datetime
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from librarian.models import BorrowedBook
from librarian.reports import (generate_monthly_report_pdf)
from django.core.mail import EmailMessage
from users.models import CustomUser


def send_due_date_reminders():
    """Send email 7 days before due date"""
    upcoming_date = timezone.now().date() + timedelta(days=7)
    books_due_soon = BorrowedBook.objects.filter(
        due_date=upcoming_date,
        return_date__isnull=True
    )

    for record in books_due_soon:
        send_mail(
            subject="📚 Reminder: Book Due Soon",
            message=f"""
Hello {record.student.first_name or record.student.email},

This is a reminder that the book "{record.book.title}" is due on {record.due_date}.
Please return it on time to avoid fines (₹5/day).

Thank you!
Library Management System
            """,
            recipient_list=[record.student.email],
            from_email=settings.DEFAULT_FROM_EMAIL,
            fail_silently=False,
        )
    print(f"Sent {books_due_soon.count()} due date reminders.")


def send_monthly_report():
    pdf_path = generate_monthly_report_pdf()
    librarian = CustomUser.objects.filter(role='librarian', is_approved=True).first()

    if not librarian:
        print("No approved librarian found.")
        return

    msg = EmailMessage(
    subject=f"📚 Monthly Library Report - {datetime.now().strftime('%B %Y')}",
    body="Please find the attached monthly library report.",
    from_email=settings.DEFAULT_FROM_EMAIL,
    to=[librarian.email]
    )
    msg.attach_file(pdf_path)
    msg.send()

    print(f"Monthly report sent to {librarian.email}")


def send_due_date_reminders():
    upcoming_date = timezone.now().date() + timedelta(days=7)
    books = BorrowedBook.objects.filter(due_date=upcoming_date, return_date__isnull=True)
    for b in books:
        send_mail(
            "📚 Reminder: Book Due Soon",
            f"Hi {b.student.email}, '{b.book.title}' is due on {b.due_date}. Return it on time!",
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