from django.contrib import admin
from django.urls import path

from work import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contacts/', views.contact_list, name='contact_list'),
    path('contacts/<int:contact_id>/', views.contact_detail, name='contact_detail'),
    path('contacts/create/', views.contact_create, name='contact_create'),
    path('contacts/<int:contact_id>/edit/', views.contact_edit, name='contact_edit'),
    path('contacts/<int:contact_id>/delete/', views.contact_delete, name='contact_delete'),
    path('search/', views.search_form, name='search_form'),
    path('search/results/', views.search_results, name='search_results'),
    
    # Authentication related routes
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Administrator only routes
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/users/<int:user_id>/promote/', views.user_promote, name='user_promote'),
    path('admin/users/<int:user_id>/demote/', views.user_demote, name='user_demote'),
    
    path('admin/', admin.site.urls),
    path('api/list/', views.listAll, name='list-all'),
    path('api/list-page/<int:page>/', views.listPaged, name='list-paged'),
    path('api/get/<int:byId>/', views.get, name='get'),
    path('api/get-detail/', views.getDetail, name='get-detail'),
    path('api/new/', views.create, name='create'),
    path('api/update/<int:byId>/', views.update, name='update'),
    path('api/delete/<int:byId>/', views.delete, name='delete'),
    path('api/search/<str:segment>/', views.search, name='search'),
]
