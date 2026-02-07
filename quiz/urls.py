from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',views.dashboard,name='dashboard'),
    path('signup/',views.signup_view,name='signup'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('create_quiz/',views.create_quiz,name='create_quiz'),
    path('quiz/<int:quiz_id>/add_question/',views.add_question,name='add_question'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    path('results/', views.my_results, name='my_results'),
    path('teacher/results/', views.teacher_results, name='teacher_results'),


]