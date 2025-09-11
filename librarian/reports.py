from datetime import datetime, timedelta
from django.db.models import Count, Sum
from django.template.loader import render_to_string
from librarian.models import Book, BorrowedBook
import weasyprint
from django.conf import settings
import os

def generate_monthly_report_pdf():
    today = datetime.now().date()
    first_day = today.replace(day=1)
    last_month = first_day - timedelta(days=1)
    start_date = last_month.replace(day=1)
    end_date = last_month

    # Most borrowed books
    top_books = BorrowedBook.objects.filter(
        issue_date__range=[start_date, end_date]
    ).values('book__title', 'book__author').annotate(
        count=Count('book')
    ).order_by('-count')[:10]

    # New books added
    new_books = Book.objects.filter(
        created_at__range=[start_date, end_date]  # Add created_at field to Book model
    )

    # Stats
    total_issued = BorrowedBook.objects.filter(
        issue_date__range=[start_date, end_date]
    ).count()

    total_fines_collected = BorrowedBook.objects.filter(
        return_date__range=[start_date, end_date]
    ).aggregate(Sum('fine'))['fine__sum'] or 0

    html = render_to_string('library/report_template.html', {
        'month': last_month.strftime("%B %Y"),
        'top_books': top_books,
        'new_books': new_books,
        'total_issued': total_issued,
        'total_fines_collected': total_fines_collected,
    })

    pdf_file = f"monthly_report_{last_month.strftime('%Y_%m')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'reports', pdf_file)

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    weasyprint.HTML(string=html).write_pdf(pdf_path)
    return pdf_path