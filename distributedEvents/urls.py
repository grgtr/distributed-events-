"""eventss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('user_handler/', include('user_handler.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from event_handler import views
from user_handler import views as user_views
from creator_handler import views as creator_views
urlpatterns = [
    # path('test/', creator_views.test, name='test'),
    path('admin/', admin.site.urls),
    path('create-event/', views.create_event, name='create_event'),

    path('event/<int:event_id>', views.current_event, name="cur_event"),
    path('event/<int:event_id>/stage/<int:stage_id>', views.current_stage, name="current_stage"),
    path('stage_registration/<int:stage_id>', views.current_stage_registration, name="current_stage_registration"),
    path('', views.show_events, name="all_events"),
    path('event/<int:event_id>/stage/<int:stage_id>/all_participants', views.show_all_participants, name="all_participants"),


    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('profile/participant_event_list', views.participant_event_list, name='participant_event_list'),
    path('profile/staff_event_list', views.staff_event_list, name='staff_event_list'),
    path('login/', auth_views.LoginView.as_view(template_name='user_handler/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='user_handler/logout.html'), name='logout'),

    path('event/<int:event_id>/edit/venue/', creator_views.venues_list, name="test"),
    path('event/<int:event_id>/edit/venue/<int:venue_id>', creator_views.edit_venue, name="edit_venue"),
    path('event/<int:event_id>/edit/venue/create', creator_views.create_venue, name="create_venue"),
    path('event/<int:event_id>/edit/venue/delete', creator_views.delete_venue, name="delete_venue"),

    path('event/<int:event_id>/edit/stages/', creator_views.stages_list, name="stages_list"),
    path('event/<int:event_id>/edit/stages/<stage_id>/end', creator_views.commit_stage, name="end_stage"),
    path('event/<int:event_id>/edit/stages/create', creator_views.create_stage, name="create_stage"),
    path('event/<int:event_id>/edit/stages/delete', creator_views.delete_stage, name="delete_stage"),
    path('event/<int:event_id>/edit/stages/edit', creator_views.edit_stage, name="edit_stage"),
    # path('event/<int:event_id>/edit/stages/', creator_views.stages_list, name="test"),

    # path('event/<int:event_id>/edit/stages/create', creator_views.create_stage, name="create_stage"),
    # path('event/<int:event_id>/edit/stages/delete', creator_views.delete_stage, name="delete_stage"),
    path('event/<int:event_id>/edit/staff', creator_views.view_staff, name="view_staff"),
    # path('event/edit/stages/add_staff', creator_views.add_staff, name="add_staff"),

    path('event/<int:event_id>/edit/participants/', creator_views.participants_list, name="participants_list"),
    path('event/<int:event_id>/edit/participants/reject', creator_views.reject_participant, name="reject_participant"),
    path('event/<int:event_id>/edit/participants/accepted', creator_views.accept_participant,
         name="accept_participant"),
    path('event/<int:event_id>/edit/participants/ban', creator_views.ban_participant, name="ban_participant"),

    path('event/<int:event_id>/edit/participants/make_newsletter', creator_views.make_newsletter, name='make_newsletter')
]

