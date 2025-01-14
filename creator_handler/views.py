from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from creator_handler.db_controller import *
from . import email
from .forms import VenueForm, StaffForm, EmailForm
from event_handler.views import error404

from json import load as json_load

import creator_handler.db_controller as c_db
import user_handler.db_controller as u_db

# from .forms import StaffForm

NAVIGATE_BUTTONS = [
    {
        'name': "Участники",
        'href': "../participants"
    },
    {
        'name': "Площадки",
        'href': "../venue"
    },
    {
        'name': "Персонал",
        'href': "../staff"
    },
    {
        'name': "Этапы",
        'href': "../stages"
    }
]


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


# @login_required
# def add_staff(request):
#     """
#     Страница добавления участника
#
#     :param request: объект с деталями запроса
#     :type request: :class: 'django.http.HttpRequest'
#     :return: html страница
#     """
#     form = StaffForm()
#     if request.method == "POST" and is_ajax(request):
#         form = StaffForm(request.POST)
#         if form.is_valid():
#             event_id = form.cleaned_data['stage'].parent
#             username = form.cleaned_data['username']
#             form.save()
#             return JsonResponse({'event_id': event_id,
#                                  'username': username,
#                                  }, status=200)
#         else:
#             return JsonResponse({'errors': form.errors.as_json()}, status=400)
#
#     return render(request, 'creator_handler/add_staff.html', {'form': form})


@login_required(login_url="login")
def participants_list(request, event_id):
    """
    Страница просмотра всех участников

    :param request: объект с деталями запроса
    :type request: :class: 'django.http.HttpRequest'
    :param event_id: id мероприятия
    :type event_id: :class: 'int'
    :return: html страница
    """
    if not user_have_access(request.user, event_id):
        return redirect('/404')
    event = get_event_by_id(event_id)
    participants_list = get_participants_by_event(event)


    context = {'participants_list': participants_list,
               "navigation_buttons": NAVIGATE_BUTTONS,
               "event": event,
               }
    return render(request, 'creator_handler/participants_list.html', context)


@login_required(login_url="login")
def reject_participant(request, event_id: int):
    if request.method == "POST" and is_ajax(request):
        user_id = request.POST.get('id', None)
        if not c_db.user_have_access(request.user, event_id, c_db.SettingsSet.EDIT_VENUES):
            return JsonResponse({"errors": "Not enough rights"}, status=400)
        try:
            c_db.reject_participant(u_db.get_user_by_id(user_id), event_id)
            return JsonResponse({}, status=200)
        except c_db.ObjectDoesNotExist:
            return JsonResponse({"errors": "There is no such venue"}, status=400)
        except Exception as e:
            print(e)  # - Заменить на логгирование
            return JsonResponse({"errors": "Undefined server error"}, status=400)
    return JsonResponse({}, status=400)


@login_required(login_url="login")
def accept_participant(request, event_id: int):
    if request.method == "POST" and is_ajax(request):
        user_id = request.POST.get('id', None)
        if not c_db.user_have_access(request.user, event_id, c_db.SettingsSet.EDIT_VENUES):
            return JsonResponse({"errors": "Not enough rights"}, status=400)
        try:
            c_db.accept_participant(u_db.get_user_by_id(user_id), event_id)
            return JsonResponse({}, status=200)
        except c_db.ObjectDoesNotExist:
            return JsonResponse({"errors": "There is no such venue"}, status=400)
        except Exception as e:
            print(e)  # - Заменить на логгирование
            return JsonResponse({"errors": "Undefined server error"}, status=400)
    return JsonResponse({}, status=400)


@login_required(login_url="login")
def ban_participant(request, event_id: int):
    if request.method == "POST" and is_ajax(request):
        user_id = request.POST.get('id', None)
        if not c_db.user_have_access(request.user, event_id, c_db.SettingsSet.EDIT_VENUES):
            return JsonResponse({"errors": "Not enough rights"}, status=400)
        try:
            c_db.ban_participant(u_db.get_user_by_id(user_id), event_id)
            return JsonResponse({}, status=200)
        except c_db.ObjectDoesNotExist:
            return JsonResponse({"errors": "There is no such venue"}, status=400)
        except Exception as e:
            print(e)  # - Заменить на логгирование
            return JsonResponse({"errors": "Undefined server error"}, status=400)
    return JsonResponse({}, status=400)


#
#
# @login_required
# def view_staff(request):
#     """
#     Страница просмотра всех участников
#
#     :param request: объект с деталями запроса
#     :type request: :class: 'django.http.HttpRequest'
#     :return: html страница
#     """
#
#     context = {}
#
#     return render(request, 'creator_handler/view_participants.html', context)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required
def view_staff(request, event_id):
    """
    Страница просмотра всех участников

    :param request: объект с деталями запроса
    :type request: :class: 'django.http.HttpRequest'
    :return: html страница
    """

    context = {
        "navigation_buttons":     [
            {
                'name': "Участники",
                'href': "participants"
            },
            {
                'name': "Площадки",
                'href': "venue"
            },
            {
                'name': "Персонал",
                'href': "staff"
            },
            {
                'name': "Этапы",
                'href': "stages"
            }
    ]}
    # context["staff_list"] = get_staff_by_stage(stage_id)

    return render(request, 'creator_handler/view_staff.html', context)


@login_required
def add_staff(request):
    """
    Страница добавления участника

    :param request: объект с деталями запроса
    :type request: :class: 'django.http.HttpRequest'
    :return: html страница
    """
    form = StaffForm()
    if request.method == "POST" and is_ajax(request):
        form = StaffForm(request.POST)
        if form.is_valid():
            event_id = form.cleaned_data['stage'].parent
            username = form.cleaned_data['username']
            form.save()
            return JsonResponse({'event_id': event_id,
                                 'username': username,
                                 }, status=200)
        else:
            return JsonResponse({'errors': form.errors.as_json()}, status=400)

    return render(request, 'creator_handler/add_staff.html', {'form': form})


def venues_list(request, event_id: int):
    if not c_db.user_have_access(request.user, event_id):
        return redirect('/404')
    all_stages = c_db.get_stages_by_event(c_db.get_event_by_id(event_id))
    #print(all_stages)
    venues_list = []
    for stage in all_stages:
        venues_from_stage  = c_db.get_venues_by_stage_id(stage.id).values_list()
        venues_list.extend(venues_from_stage)
    #print(venues_list)
    event = get_event_by_id(event_id)
    context = {
        "venues_list": venues_list,
        "navigation_buttons": NAVIGATE_BUTTONS,
        "event": event,
    }
    return render(request, 'creator_handler/venues_list.html', context)


@login_required(login_url="login")
def delete_venue(request, event_id: int):
    if request.method == "POST" and is_ajax(request):
        venue_id = request.POST.get('id', None)
        if not c_db.user_have_access(request.user, event_id, c_db.SettingsSet.EDIT_VENUES):
            return JsonResponse({"errors": "Not enough rights"}, status=400)
        try:
            c_db.Venue.objects.get(id=venue_id).delete()
            return JsonResponse({}, status=200)
        except c_db.ObjectDoesNotExist:
            return JsonResponse({"errors": "There is no such venue"}, status=400)
        except Exception as e:
            print(e)  # - Заменить на логгирование
            return JsonResponse({"errors": "Undefined server error"}, status=400)
    return JsonResponse({}, status=400)


@login_required(login_url="login")
def create_venue(request, event_id: int):
    if not c_db.user_have_access(request.user, event_id, c_db.SettingsSet.EDIT_VENUES):
        return redirect("/404")
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            region = form.cleaned_data['region']
            participants_maximum = form.cleaned_data['participants_maximum']
            contacts = form.cleaned_data['contacts']
            c_db.create_venue(
                name,
                address,
                region,
                participants_maximum,
                contacts,
                event_id
            )
            return redirect(f'/events/{event_id}/edit/venue/')
    else:
        form = VenueForm()
    context = {
        "form": form,
    }
    return render(request, 'creator_handler/create_venue.html', context)


@login_required(login_url="login")
def edit_venue(request, event_id: int, venue_id: int):
    if not (c_db.user_have_access(request.user, event_id,
                                  c_db.SettingsSet.EDIT_VENUES) and c_db.is_venue_attached_to_event(event_id,
                                                                                                    venue_id)):
        return redirect("/404")
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            region = form.cleaned_data['region']
            participants_maximum = form.cleaned_data['participants_maximum']
            contacts = form.cleaned_data['contacts']
            c_db.edit_venue(name, address, region, participants_maximum, contacts, venue_id)
            return redirect(f'event/{event_id}/edit/venue/')
    else:
        venue_data = c_db.get_venue_by_id_dict(venue_id)

        form = VenueForm(venue_data)
    context = {
        "form": form,
        "saved_form": venue_data,
    }
    return render(request, 'creator_handler/edit_venue.html', context)


@login_required
def make_newsletter(request, event_id: int):
    # if not c_db.user_have_access(request.user, event_id, c_db.SettingsSet.EDIT_VENUES):
    #     return redirect("/404")
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            text = form.cleaned_data['text']
            email.send_message(c_db.get_participants_by_event(get_event_by_id(event_id)), text, subject)
            return redirect(f'/events/edit/{event_id}/participants/')
    form = EmailForm()
    return render(request, 'creator_handler/create_newsletter.html', {"form": form})


@login_required(login_url="login")
def stages_list(request, event_id: int):
    if not user_have_access(request.user, event_id):
        return error404(request)

    context = {
        "navigation_buttons": NAVIGATE_BUTTONS,
        'stages_list': get_formatted_stages(event_id),
        "event": get_event_by_id(event_id)
    }
    return render(request, 'creator_handler/stages_list.html', context)


@login_required(login_url="login")
def create_stage(request, event_id: int):
    if not user_have_access(request.user, event_id):
        return error404(request)
    if request.method != "POST":
        return JsonResponse({}, status=403)
    try:
        next_stage = get_stage_by_id(json_load(request)["next_stage_id"])
        make_record_stage("Новый этап", get_event_by_id(event_id), next_stage=next_stage)
        return JsonResponse({}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"errors": "undefined"}, status=500)


@login_required(login_url="login")
def delete_stage(request, event_id: int):
    if not user_have_access(request.user, event_id):
        return error404(request)
    if request.method != "POST":
        return JsonResponse({}, status=403)
    try:
        stage_id = json_load(request)["stage_id"]
        delete_stage_recursive(stage_id)
        return JsonResponse({}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"errors": "undefined"}, status=500)


@login_required(login_url="login")
def edit_stage(request, event_id: int):
    if not user_have_access(request.user, event_id):
        return error404(request)
    if request.method != "POST":
        return JsonResponse({}, status=403)
    try:
        request = json_load(request)
        stage_id = request["stage_id"]
        name = request["name"]
        description = request["description"]
        contacts = request["contacts"]
        # can_register = json_load(request)["can_register"]
        can_register = True
        update_stage(stage_id, name, description, contacts, can_register)
        return JsonResponse({}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"errors": "undefined"}, status=500)



@login_required(login_url="login")
def commit_stage(request, event_id, stage_id):
    stage = get_stage_by_id(stage_id)
    if not user_have_access(request.user, event_id) or event_id != get_event_by_stage(stage).id:
        return error404(request)
    # if request.method != "POST":
    #     return JsonResponse({}, status=403)
    try:
        end_stage(stage, 1)
        return JsonResponse({}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({'errors': "something went wrong"}, status=500)