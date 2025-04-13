from django.urls import path
from . import views

urlpatterns = [
    path('', views.groster_landing, name='groster_landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/delete/<int:group_id>/', views.group_delete, name='group_delete'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/invite/', views.invite_to_group, name='invite_to_group'),
    path('groups/invite/accept/<str:token>/', views.accept_invitation, name='accept_invitation'),
    path('groups/join/<int:group_id>/', views.join_group, name='join_group'),
    path('groups/leave/<int:group_id>/', views.leave_group, name='leave_group'),
    path('grocery/', views.grocery_list, name='grocery_list'),
    path('grocery/create/', views.grocery_create, name='grocery_create'),
    path('grocery/delete/<int:item_id>/', views.grocery_delete, name='grocery_delete'),
    path('basket/', views.basket_view, name='basket_view'),
    path('basket/add/<int:item_id>/', views.add_to_basket, name='add_to_basket'),
    path('basket/remove/<int:item_id>/', views.remove_from_basket, name='remove_from_basket'),
]