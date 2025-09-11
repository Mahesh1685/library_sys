from django.urls import path
from librarian import views

urlpatterns = [
    path('dashboard/', views.librarian_dashboard, name='librarian_dashboard'),
    path('add/', views.add_book, name='add_book'),
    path('edit/<int:pk>/', views.edit_book, name='edit_book'),
    path('delete/<int:pk>/', views.delete_book, name='delete_book'),
    path('return/<int:pk>/',views.return_book, name='return_book'),
    path('books/', views.book_list, name='book_list'),
    path('profile/', views.student_profile, name='student_profile'),
    path('approve/',views.approve_students, name='approve_students'),
    path('revoke/<int:pk>/', views.revoke_student, name='revoke_student'),
    path('request-borrow/<int:book_id>/', views.request_borrow, name='request_borrow'),
    path('approve-request/<int:request_id>/', views.approve_borrow_request, name='approve_borrow_request'),
]