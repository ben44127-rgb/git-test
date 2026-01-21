from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('delete/', views.delete_user, name='delete'),
    path('check/', views.check_auth, name='check_auth'),
]
