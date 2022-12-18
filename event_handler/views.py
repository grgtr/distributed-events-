from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from event_handler.forms import Event
from event_handler.models import Event, Stage

from event_handler.db_controller import *


@login_required
def create_event(request):
    """
    Страница создания мероприятия

    :param request: объект с деталями запроса
    :type request: :class: 'django.http.HttpRequest'
    :return: html страница
    """
    context = {'page-name': "Создать мероприятие",
               'navigation_buttons': [
                   {
                       'name': "Главная",
                       'href': ".."
                   },
                   {
                       'name': "Профиль",
                       'href': "/user_profile"
                   }
               ]
               }
    if request.method == 'POST':
        form = EventForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            # privacy = form.cleaned_data['privacy']
            preview = form.cleaned_data['preview']
            date_start = form.cleaned_data['date_start']
            date_finish = form.cleaned_data['date_finish']
            description = form.cleaned_data['description']

            user = request.user

            if user.is_authenticated:
                record = Event(name=name, description=description)
                record.save()
                event = Event.objects.create(name=name, description=description)
                record = Stage(
                    name=name,
                    parent=event,
                    preview=preview,
                    time_start=date_start,
                    time_end=date_finish,
                    description=description
                )
                record.save()
        else:
            return HttpResponse('Invalid data')
    context['form'] = EventForm()

    return render(request, 'creator_handler/create_event.html', context)


def all_events(request, page_number=1):
    """
    Страница всех мероприятий

    :param request: объект с деталями запроса
    :type request: :class: 'django.http.HttpRequest'
    :return: html страница
    """

    event_list = get_all_events(int(page_number), request.user)

    # if not event_list:
    #     return error404(request)

    context = {'page-name': 'Все мероприятия',
               'event_list': event_list,
               'navigation_buttons': [
                   {
                       'name': "О нас",
                       'href': "https://hsse.mipt.ru/"
                   },
                   {
                       'name': "Создать мероприятие",
                       'href': "/create_event"
                   },
                   {
                       'name': "Профиль",
                       'href': "/user_profile"
                   }
               ]
               }

    return render(request, 'event_handler/all_events.html', context)


def current_event(request, event_id):
    """
    Страница одного мероприятия

    :param request: объект с деталями запроса
    :type request: :class: 'django.http.HttpRequest'
    :param event_id: id мероприятия
    :type event_id: :class: 'int'
    :return: html страница
    """
    try:
        event = get_event_by_id(event_id)
        context = {'page-name': f'{event.name}', 'navigation_buttons': [
            {
                'name': "Главная",
                'href': ".."
            },
            {
                'name': "Зарегистрироваться",
                'href': f"../event_registration/{event_id}"
            },
            {
                'name': "Профиль",
                'href': "/user_profile"
            }
        ]
                   }
        event = get_event_by_id(event_id)
        context['event_id'] = event_id
        context['name'] = event.name
        context['page-name'] = context['name']
        context['description'] = event.description
        context['stages'] = [get_stages_by_event(context["event_id"])]
        return render(request, 'event_handler/event.html', context)
    except ValueError:
        raise Http404

