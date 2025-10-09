#Url handling for project

from django.urls import path
from librarian import views

urlpatterns = [
    path('dashboard/', views.librarian_dashboard, name='librarian_dashboard'), #navigates to librarian dashboard
    path('add/', views.add_book, name='add_book'), #navigates to adding a book
    path('edit/<int:pk>/', views.edit_book, name='edit_book'), #navigates to edit a book based on primary id
    path('delete/<int:pk>/', views.delete_book, name='delete_book'), #navigates to delete a book  based on primary id
    path('return/<int:pk>/',views.return_book, name='return_book'), #navigates to returned book based on primary id
    path('books/', views.book_list, name='book_list'), #navigates to see the book list
    path('profile/', views.student_profile, name='student_profile'), #navigates to student profile
    path('approve/',views.approve_students, name='approve_students'), #navigates to approve a student
    path('revoke/<int:pk>/', views.revoke_student, name='revoke_student'), #navigates to revoke a student's permission
    path('request-borrow/<int:book_id>/', views.request_borrow, name='request_borrow'), #navigates to request to borrow a book
    path('approve-request/<int:request_id>/', views.approve_borrow_request, name='approve_borrow_request'), # navigates to approve the borrow request
    path('mark-handover/<int:pk>/', views.mark_handover, name='mark_handover'), #navigates to mark handover books to student physically
]