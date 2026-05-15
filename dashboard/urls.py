from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.events, name='events'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('sources/', views.sources, name='sources'),
    path('sources/<int:pk>/', views.source_detail, name='source_detail'),
    path('groups/', views.groups, name='groups'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/sources/', views.admin_sources, name='admin_sources'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('graph-data/', views.graph_data, name='graph_data'),

    path('run/collect/', views.run_collect, name='run_collect'),
    path('run/process/', views.run_process, name='run_process'),
    path('run/cluster/', views.run_cluster, name='run_cluster'),
    path('run/graph/', views.run_graph, name='run_graph'),
]


