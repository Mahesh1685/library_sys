from django.urls import path
from users import views

urlpatterns = [
    path('', views.home, name='home'), #for displaying home page
    path('register/', views.register, name='register'), #for displaying registration page
    path('login/', views.login_view, name='login'), #for displaying login page
    path('logout/', views.logout_view, name='logout'), #for logout after the session is expired
]