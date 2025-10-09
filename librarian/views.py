#for some logics in library

from django.shortcuts import render, redirect, get_object_or_404 #for templates,urls,get an item or return error
from django.contrib.auth.decorators import login_required #login required for certain things
from django.contrib import messages #for messages to be displayed
from django.core.mail import send_mail #for sending emails to student
from django.conf import settings #to use some django's settings(inbuilt)
from librarian.models import Book, BorrowedBook, BorrowRequest, QuestionPaper #using books and resources from models
from librarian.forms import BookForm #handling form
from users.models import CustomUser  #for user's separate data for dashboard
from django.utils import timezone #for handling due date,fine handling and more
from django.db.models import Q  # for searching books
import logging #making loging easier

# Set up logger
logger = logging.getLogger(__name__)

@login_required
def librarian_dashboard(request): #logics for librarian dashboard
    if request.user.role != 'librarian':
        return redirect('login') #returns to login page if user is not librarian

    books = Book.objects.all() #displays all books present in the library
    borrowed_books = BorrowedBook.objects.filter(return_date__isnull=True) #displays borrowed books
    pending_students = CustomUser.objects.filter(role='student', pending_approval=True) #displays pending students for registration
    approved_students = CustomUser.objects.filter(role='student', is_approved=True).order_by('year_of_study', 'username') #displays approved students
    pending_requests = BorrowRequest.objects.filter(status='pending') #displays pending request for borrowing

    return render(request, 'librarian_dashboard.html', {
        'books': books,
        'borrowed_books': borrowed_books,
        'pending_students': pending_students,
        'approved_students': approved_students,
        'pending_requests': pending_requests,
    }) #returns html template that contains books,borrowed books,pending students,approved students,pending requests

@login_required
def approve_students(request): #logics for approving a student after registration
    if request.user.role != 'librarian':
        messages.error(request, "Access denied.")
        return redirect('login') #returns to login page if user is not librarian

    pending_students = CustomUser.objects.filter(role='student', pending_approval=True)

    if request.method == "POST":
        user_id = request.POST.get('user_id') #displays student's id (email)
        action = request.POST.get('action') #what step to be taken i.e. approve or decline the student
        student = get_object_or_404(CustomUser, id=user_id) #can search for student based on id

        if action == "approve":
            username = request.POST.get('username') #librarian can only approve if username is assigned to that student
            if not username:
                messages.error(request, "Username is required.")
            elif CustomUser.objects.filter(username=username).exists():
                messages.error(request, "Username taken.") #if username is already taken this message will be displayed
            else:
                student.username = username
                student.is_approved = True #if username is assigned (student will be auto approved)
                student.pending_approval = False
                student.save()  #data will be saved

                try:
                    send_mail(
                        subject=" Library Account Approved",
                        message=f"Hello {student.email},\n\nYour library account has been approved!\nUsername: {username}\n\nThank you!",
                        recipient_list=[student.email],
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        fail_silently=False,
                    )
                    messages.success(request, f"Approved {student.email} as '{username}'")
                except Exception as e:
                    messages.warning(request, f"Approved but failed to send email: {e}") #sends email to student as username assigned with error handling try except blocks

        elif action == "decline":
            student.delete()
            messages.info(request, f"Declined {student.email}")

        return redirect('approve_students')

    return render(request, 'approve_students.html', {
        'pending_students': pending_students
    })

@login_required
def add_book(request): #logics for adding a book
    if request.user.role != 'librarian':
        return redirect('login') #only librarian can add a book

    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.available_copies = book.total_copies #assigns total copies as available copies
            book.save()  #saves the book
            messages.success(request, "Book added!")
            return redirect('librarian_dashboard')
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})

@login_required #only librarian can edit book
def edit_book(request, pk): #logics for editing a book
    book = get_object_or_404(Book, pk=pk) #used to search a book based on its primary id
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid(): #used to check whether the details in the given form is valid
            form.save() #saves the updated details of the book
            messages.success(request, "Book updated!")
            return redirect('librarian_dashboard')
    else:
        form = BookForm(instance=book)
    return render(request, 'edit_book.html', {'form': form, 'book': book})

@login_required
def delete_book(request, pk): #logics for deleting a book
    book = get_object_or_404(Book, pk=pk)
    if book.available_copies == book.total_copies: #used to check whether any copies are issued before deleting
        book.delete() #whether it is none (we can delete)
        messages.success(request, "Book deleted.")
    else:
        messages.error(request, "Cannot delete — copies are issued.")
    return redirect('librarian_dashboard')

def book_list(request): #logics for searching a book
    query = request.GET.get('q')
    books = Book.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) | #if any letter in title matches the searching letter
            Q(author__icontains=query) | #if any letter in author matches the searching letter
            Q(isbn__icontains=query) #if any letter in isbn code of the book matches the searching letter
        ) #if everything is matched also it will return a result
    return render(request, 'book_list.html', {'books': books, 'query': query})

@login_required
def return_book(request, pk): #logics for return book
    borrowed_book = get_object_or_404(BorrowedBook, pk=pk) #search based on borrowed book primary id
    borrowed_book.return_date = timezone.now().date() #for time calculations for return date
    borrowed_book.save()
    borrowed_book.book.available_copies+=1 #after returning copies will be increased
    borrowed_book.book.save()
    return redirect('librarian_dashboard')


@login_required
def student_profile(request):
    if request.user.role != 'student':
        return redirect('login')

    books = Book.objects.filter(available_copies__gt=0) #displays books with available copies gt than 0
    pending_request = BorrowRequest.objects.filter(student=request.user, status='pending') #displays pending borrow request
    issued_request = BorrowedBook.objects.filter(student=request.user) #displays issued books
    pending_request_book_ids = pending_request.values_list('book_id', flat=True) #books that are with pending request with no copy
    total_due = sum(b.fine for b in issued_request) #calculates total due
    department=request.user.department #gets department name
    question_papers=QuestionPaper.objects.filter(department=department).order_by('semester','subject') #for displaying qn papers based on dept wise and ordering sem wise

    return render(request, 'student_profile.html', {
        'books': books,
        'pending_request': pending_request,
        'issued_request': issued_request,
        'total_due': total_due,
        'pending_request_book_ids': pending_request_book_ids,
        'question_papers': question_papers,
    })

@login_required
def revoke_student(request, pk): #logics for revoking a student's permission who is in using Library Management System
    if request.user.role != 'librarian':
        return redirect('home')

    student = get_object_or_404(CustomUser, pk=pk, role='student')
    student.is_approved = False
    student.is_active = False
    student.save()
    messages.info(request, f"Access revoked for {student.username}")
    return redirect('librarian_dashboard')

@login_required
def request_borrow(request, book_id): #logics for requesting to borrow a book
    if request.user.role != 'student':
        return redirect('home')

    book = get_object_or_404(Book, id=book_id)

    if book.available_copies <= 0: #if no copies available
        messages.error(request, "No copies available.")
        return redirect('student_profile')

    if BorrowRequest.objects.filter(student=request.user, book=book, status='pending').exists(): #if borrow requests is already requested
        messages.info(request, "Already requested.")
    else:
        BorrowRequest.objects.create(student=request.user, book=book)
        messages.success(request, f"Request sent for '{book.title}'.")

    return redirect('student_profile')

@login_required
def approve_borrow_request(request, request_id): #logics for approving borrow request
    if request.method != "POST":
        return redirect('librarian_dashboard')

    if request.user.role != 'librarian':
        messages.error(request, "Access denied.")
        return redirect('home')

    try:
        req = get_object_or_404(BorrowRequest, id=request_id)

        if req.status == 'pending':
            #Create BorrowedBook (copies handled in save())
            BorrowedBook.objects.create(
                student=req.student,
                book=req.book,
                issue_date=timezone.now().date(),
                due_date=timezone.now().date() + timezone.timedelta(days=14),
                fine=0.00
            )

            #Mark request as approved
            req.status = 'approved'
            req.save()

            messages.success(request, f" '{req.book.title}' issued to {req.student.username}")
        else:
            messages.info(request, "Request already processed.")

    except Exception as e:
        error_msg = f"Error: {type(e).__name__}: {e}"
        messages.error(request, error_msg)
        print("ERROR:", error_msg)

    return redirect('librarian_dashboard')

@login_required
def mark_handover(request, pk): #logics for marking handover a book physically to student
    if request.user.role != 'librarian':
        return redirect('home')

    borrowed_book = get_object_or_404(BorrowedBook, pk=pk)

    if not borrowed_book.handover_date:
        # Set handover date to today
        borrowed_book.handover_date = timezone.now().date()
        # Reset due date from handover
        borrowed_book.due_date = borrowed_book.handover_date + timezone.timedelta(days=14)
        borrowed_book.save()

        messages.success(request, f" '{borrowed_book.book.title}' marked as handed over. Due: {borrowed_book.due_date}")

    return redirect('librarian_dashboard')