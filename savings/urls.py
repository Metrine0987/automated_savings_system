from django.urls import path
from .import views


app_name ='savings'

urlpatterns = [
    path('', views.home , name='home'),
    path('register/', views.register, name='register'),
    path('login_page/', views.login_page, name='login_page'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
     path('create_goal/', views.create_goal, name='create_goal'),
     path('delete_goal/<int:goal_id>/', views.delete_goal, name='delete_goal'),
    path('edit_goal/<int:goal_id>/', views.edit_goal, name='edit_goal'),
    path('set_recurring_savings/', views.set_recurring_savings, name='set_recurring_savings'),
]