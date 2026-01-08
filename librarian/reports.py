#file for handling how the pdf monthly report to be submitted as

from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from librarian.models import BorrowedBook, Book
from django.db.models import Sum,Count
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_monthly_report_pdf():
    """
    Generate a professional monthly PDF report using ReportLab.
    """
    # Get last month's date range
    today = timezone.now().date()
    first_day = today.replace(day=1)
    last_month = first_day - timedelta(days=1)
    start_date = last_month.replace(day=1)
    end_date = last_month

    # Stats
    total_issued = BorrowedBook.objects.filter(
        issue_date__range=[start_date, end_date]
    ).count()

    total_fines_collected = BorrowedBook.objects.filter(
        return_date__range=[start_date, end_date]
    ).aggregate(fine_sum=Sum('fine'))['fine_sum'] or 0

    total_books = Book.objects.count()

    # Top 10 borrowed books
    top_books = BorrowedBook.objects.filter(
        issue_date__range=[start_date, end_date]
    ).values('book__title', 'book__author').annotate(
        count=Count('book')
    ).order_by('-count')[:10]

    # New books added
    new_books = Book.objects.filter(
        created_at__range=[start_date, end_date]
    )

    # Create folder if not exists
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    os.makedirs(pdf_dir, exist_ok=True)

    pdf_file = f"monthly_report_{last_month.strftime('%Y_%m')}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_file)

    # Create PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("Library Management System", styles['Title'])
    subtitle = Paragraph(f"Monthly Activity Report - {last_month.strftime('%B %Y')}", styles['Heading1'])
    generated = Paragraph(f"Generated on: {timezone.now().strftime('%B %d, %Y at %H:%M')}", styles['Normal'])

    elements.append(title)
    elements.append(Spacer(1, 12))
    elements.append(subtitle)
    elements.append(Spacer(1, 12))
    elements.append(generated)
    elements.append(Spacer(1, 20))

    # Summary Table
    summary_data = [
        ["Total Books", "Books Issued", "Fines Collected", "New Books Added"],
        [str(total_books), str(total_issued), f"₹{total_fines_collected:.2f}", str(new_books.count())]
    ]

    summary_table = Table(summary_data, colWidths=[150, 150, 150, 150])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3498db")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 30))

    # Top Books Table
    if top_books:
        elements.append(Paragraph("🏆 Most Borrowed Books (Top 10)", styles['Heading2']))
        elements.append(Spacer(1, 12))

        book_data = [["Rank", "Title", "Author", "Count"]]
        for i, book in enumerate(top_books, 1):
            book_data.append([str(i), book['book__title'], book['book__author'], str(book['count'])])

        t = Table(book_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))

    # New Books Table
    if new_books:
        elements.append(Paragraph("🆕 New Books Added This Month", styles['Heading2']))
        elements.append(Spacer(1, 12))

        new_data = [["Title", "Author", "ISBN", "Copies"]]
        for book in new_books:
            new_data.append([book.title, book.author, book.isbn, str(book.total_copies)])

        t2 = Table(new_data)
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#27ae60")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t2)
        elements.append(Spacer(1, 20))

    # Build PDF
    doc.build(elements)

    print(f"✅ Monthly report saved at: {pdf_path}")
    return pdf_path