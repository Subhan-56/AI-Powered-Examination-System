from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_exam, name='create_exam'),
    path('<int:exam_id>/add-question/', views.add_question, name='add_question'),
    path('<int:exam_id>/publish/', views.publish_exam, name='publish_exam'),
    path('<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    path('my-exams/', views.my_exams, name='my_exams'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
]


