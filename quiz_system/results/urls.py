from django.urls import path
from . import views

urlpatterns = [
    path('available/', views.available_exams, name='available_exams'),
    path('start/<int:exam_id>/', views.start_exam, name='start_exam'),
    path('submit/<int:attempt_id>/', views.submit_exam, name='submit_exam'),
    path('result/<int:attempt_id>/', views.view_result, name='view_result'),
    path('exam/<int:exam_id>/all-results/', views.exam_results, name='exam_results'),
]
