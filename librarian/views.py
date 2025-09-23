# librarian/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from librarian.models import Book, BorrowedBook, BorrowRequest, QuestionPaper
from librarian.forms import BookForm
from users.models import CustomUser  # Make sure this is correct
from django.utils import timezone
from django.db.models import Q  # ✅ Added: for search
import logging

# Set up logger
logger = logging.getLogger(__name__)

@login_required
def librarian_dashboard(request):
    if request.user.role != 'librarian':
        return redirect('login')

    books = Book.objects.all()
    borrowed_books = BorrowedBook.objects.filter(return_date__isnull=True)
    pending_students = CustomUser.objects.filter(role='student', pending_approval=True)
    approved_students = CustomUser.objects.filter(role='student', is_approved=True).order_by('year_of_study', 'username')
    pending_requests = BorrowRequest.objects.filter(status='pending')

    return render(request, 'librarian_dashboard.html', {
        'books': books,
        'borrowed_books': borrowed_books,
        'pending_students': pending_students,
        'approved_students': approved_students,
        'pending_requests': pending_requests,
    })

@login_required
def approve_students(request):
    if request.user.role != 'librarian':
        messages.error(request, "Access denied.")
        return redirect('login')

    pending_students = CustomUser.objects.filter(role='student', pending_approval=True)

    if request.method == "POST":
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        student = get_object_or_404(CustomUser, id=user_id)

        if action == "approve":
            username = request.POST.get('username')
            if not username:
                messages.error(request, "Username is required.")
            elif CustomUser.objects.filter(username=username).exists():
                messages.error(request, "Username taken.")
            else:
                student.username = username
                student.is_approved = True
                student.pending_approval = False
                student.save()

                try:
                    send_mail(
                        subject="✅ Library Account Approved",
                        message=f"Hello {student.email},\n\nYour library account has been approved!\nUsername: {username}\n\nThank you!",
                        recipient_list=[student.email],
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        fail_silently=False,
                    )
                    messages.success(request, f"Approved {student.email} as '{username}'")
                except Exception as e:
                    messages.warning(request, f"Approved but failed to send email: {e}")

        elif action == "decline":
            student.delete()
            messages.info(request, f"Declined {student.email}")

        return redirect('approve_students')

    return render(request, 'approve_students.html', {
        'pending_students': pending_students
    })

@login_required
def add_book(request):
    if request.user.role != 'librarian':
        return redirect('login')

    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.available_copies = book.total_copies
            book.save()
            messages.success(request, "Book added!")
            return redirect('librarian_dashboard')
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})

@login_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated!")
            return redirect('librarian_dashboard')
    else:
        form = BookForm(instance=book)
    return render(request, 'edit_book.html', {'form': form, 'book': book})

@login_required
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.available_copies == book.total_copies:
        book.delete()
        messages.success(request, "Book deleted.")
    else:
        messages.error(request, "Cannot delete — copies are issued.")
    return redirect('librarian_dashboard')

def book_list(request):
    query = request.GET.get('q')
    books = Book.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )
    return render(request, 'book_list.html', {'books': books, 'query': query})

@login_required
def return_book(request, pk):
    borrowed_book = get_object_or_404(BorrowedBook, pk=pk)
    borrowed_book.return_date = timezone.now().date()
    borrowed_book.save()
    borrowed_book.book.available_copies+=1
    borrowed_book.book.save()
    return redirect('librarian_dashboard')


@login_required
def student_profile(request):
    if request.user.role != 'student':
        return redirect('login')

    books = Book.objects.filter(available_copies__gt=0)
    pending_request = BorrowRequest.objects.filter(student=request.user, status='pending')
    issued_request = BorrowedBook.objects.filter(student=request.user)
    pending_request_book_ids = pending_request.values_list('book_id', flat=True)
    total_due = sum(b.fine for b in issued_request)
    department=request.user.department
    question_papers=QuestionPaper.objects.filter(department=department).order_by('semester','subject')

    return render(request, 'student_profile.html', {
        'books': books,
        'pending_request': pending_request,
        'issued_request': issued_request,
        'total_due': total_due,
        'pending_request_book_ids': pending_request_book_ids,
        'question_papers': question_papers,
    })

@login_required
def revoke_student(request, pk):
    if request.user.role != 'librarian':
        return redirect('home')

    student = get_object_or_404(CustomUser, pk=pk, role='student')
    student.is_approved = False
    student.is_active = False
    student.save()
    messages.info(request, f"Access revoked for {student.username}")
    return redirect('librarian_dashboard')

@login_required
def request_borrow(request, book_id):
    if request.user.role != 'student':
        return redirect('home')

    book = get_object_or_404(Book, id=book_id)

    if book.available_copies <= 0:
        messages.error(request, "No copies available.")
        return redirect('student_profile')

    if BorrowRequest.objects.filter(student=request.user, book=book, status='pending').exists():
        messages.info(request, "Already requested.")
    else:
        BorrowRequest.objects.create(student=request.user, book=book)
        messages.success(request, f"Request sent for '{book.title}'.")

    return redirect('student_profile')

@login_required
def approve_borrow_request(request, request_id):
    if request.method != "POST":
        return redirect('librarian_dashboard')

    if request.user.role != 'librarian':
        messages.error(request, "Access denied.")
        return redirect('home')

    try:
        req = get_object_or_404(BorrowRequest, id=request_id)

        if req.status == 'pending':
            # ✅ Create BorrowedBook (copies handled in save())
            BorrowedBook.objects.create(
                student=req.student,
                book=req.book,
                issue_date=timezone.now().date(),
                due_date=timezone.now().date() + timezone.timedelta(days=14),
                fine=0.00
            )

            # ✅ Mark request as approved
            req.status = 'approved'
            req.save()

            messages.success(request, f"✅ '{req.book.title}' issued to {req.student.username}")
        else:
            messages.info(request, "Request already processed.")

    except Exception as e:
        error_msg = f"Error: {type(e).__name__}: {e}"
        messages.error(request, error_msg)
        print("🚨 ERROR:", error_msg)

    return redirect('librarian_dashboard')

@login_required
def mark_handover(request, pk):
    if request.user.role != 'librarian':
        return redirect('home')

    borrowed_book = get_object_or_404(BorrowedBook, pk=pk)

    if not borrowed_book.handover_date:
        # Set handover date to today
        borrowed_book.handover_date = timezone.now().date()
        # Reset due date from handover
        borrowed_book.due_date = borrowed_book.handover_date + timezone.timedelta(days=14)
        borrowed_book.save()

        messages.success(request, f"✅ '{borrowed_book.book.title}' marked as handed over. Due: {borrowed_book.due_date}")

    return redirect('librarian_dashboard')