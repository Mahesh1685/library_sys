#file for handling how the pdf monthly report to be submitted as

from datetime import datetime, timedelta
from django.db.models import Count, Sum
from django.template.loader import render_to_string
from librarian.models import Book, BorrowedBook
import weasyprint #to convert html page into a pdf for a report
from django.conf import settings
import os

def generate_monthly_report_pdf(): #generates a pdf every first day of every month
    today = datetime.now().date() #gets today's date
    first_day = today.replace(day=1) #replace today's date as 1 and assigns to first day
    last_month = first_day - timedelta(days=1) #subtracts the first day with one day and assigns it to last month i.e.one day before today ;as today assigned as 1 ;it gets to previous month
    start_date = last_month.replace(day=1) #on previous month last date is replaced as first date of that month
    end_date = last_month

    # Most borrowed books
    top_books = BorrowedBook.objects.filter(
        issue_date__range=[start_date, end_date]
    ).values('book__title', 'book__author').annotate(
        count=Count('book')
    ).order_by('-count')[:10]

    # New books added
    new_books = Book.objects.filter(
        created_at__range=[start_date, end_date]
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