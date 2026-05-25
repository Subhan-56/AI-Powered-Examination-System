from django.urls import path
from . import views

urlpatterns = [
    path('exam/<int:exam_id>/generate/', views.generate_questions, name='generate_questions'),
    path('exam/<int:exam_id>/review/', views.review_questions, name='review_questions'),
    path('exam/<int:exam_id>/approve/', views.approve_questions, name='approve_questions'),
]

