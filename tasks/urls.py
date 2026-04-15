from django.urls import path
from . import views
 
app_name = 'tasks'
 
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.task_list, name='task_list'),
    path('analytics/', views.analytics, name='analytics'),
    path('api/parse-voice/', views.parse_voice, name='parse_voice'),
    path('api/create/', views.create_task, name='create_task'),
    path('api/tasks/', views.get_tasks_json, name='get_tasks'),
    path('api/tasks/<int:task_id>/status/', views.update_task_status, name='update_status'),
]
 

