from user_handler.models import User, PersonalData
from event_handler.models import Stage, Event, StageStaff, StageParticipants

from user_handler.db_controller import create_user_for_django_user

from django.contrib.auth.admin import User as DjangoUser
from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from typing import Union, List, Tuple, Set

from itertools import chain

from collections import namedtuple

ITEMS_PER_PAGE = 12  # Количество объектов в одной странице выдачи

import itertools


def get_list_results_by_stage(stage_id: int):
    info_stage = get_stage_by_id(stage_id)
    # participants = StageParticipants.objects.filter(stage=stage_id).values_list('user', 'role', 'score')
    # participants = StageParticipants.objects.filter(stage=stage_id).order_by('score').values_list('user', 'role', 'score').reverse()
    participants = StageParticipants.objects.filter(stage=stage_id).order_by('-role', '-score')
    answer = []
    for index, participant in enumerate(participants):
        role = ""
        if participant.role == 0:
            role = "Участник"
        elif participant.role == 10:
            role = "Призер"
        else:
            role = "Победитель"
        list = namedtuple("namedtuplelist", "num name_all status_score total_score")
        # answer.append((index + 1, participant.user.personal_data, role, participant.score))
        answer.append(list(num=(index + 1), name_all=(participant.user.personal_data), status_score=(role),
                           total_score=(participant.score)))
    # (user, role, score)
    # print(participants, "participants")
    return answer


def get_info_event(event_id: int) -> Union[Event]:
    """
    Получить информацию о мероприятии по его id
    :param event_id: Идентификатор мероприятия
    :return: Мероприятие
    """
    try:
        event = Event.objects.get(pk=event_id)
        return event
    except ObjectDoesNotExist:
        return None


def get_open_or_closed_events(django_user: DjangoUser = None, is_open: bool = True) -> Union[
    List, Union[Tuple, Event, int]]:
    """
    Получить список открытых или закрытых мероприятий по заданным параметрам
    :param django_user: Пользователь, сделавший запрос
    :return: Список из пар: мероприятие, bool участвует ли django_user в этом мероприятии

    """

    user_events = set()
    if (not django_user.is_anonymous) and django_user is not None:
        user = get_user_by_django_user(django_user)
        user_events = get_user_events(user)

    result = list()
    stages = Stage.objects.filter(settings__can_register=is_open)
    parent_events_id = stages.values_list('parent', flat=True).distinct()
    parents_event = Event.objects.filter(id__in=parent_events_id)

    for event in parents_event:
        if event in user_events:
            result.append((event, True))
        else:
            result.append((event, False))
    return result


def get_all_events(django_user: DjangoUser = None) -> Union[List, Union[Tuple, Event, Stage, int]]:
    """
    Получить список всех мероприятий по заданным параметрам
    :param django_user: Пользователь, сделавший запрос
    :return: Список из троек: мероприятие, его первый этап, bool участвует ли django_user в этом мероприятии

    """

    user_events = set()
    if (not django_user.is_anonymous) and django_user is not None:
        user = get_user_by_django_user(django_user)
        user_events = get_user_events(user)

    result = list()
    events = Event.objects.all()
    for event in events:
        if event in user_events:
            result.append((event, event.stage_set.first, True))
        else:
            result.append((event, event.stage_set.first, False))
    return result


def get_user_events(user: User, user_role=0) -> Union[Set, int]:
    """
    :param user: Пользователь. Удивительно, да?
    :param user_role: Роль пользователя. (0 - все, 1 - участник, 2 - модератор)
    :return: Множество мероприятий, в которых участвует user
    """
    result = set()
    stages = get_user_stages(user, user_role)
    for stage in stages:
        result.add(stage.stage.parent)
    return result


def get_user_stages(user: User, user_role=0):
    """
    :param user: Пользователь. Удивительно, да?
    :param user_role: Роль пользователя. (0 - все, 1 - участник, 2 - модератор)
    :return: Список этапов, в которых участвует user
    """
    if user_role == 0:
        stages = list(chain(user.stageparticipants_set.all(), user.stagestaff_set.all()))
    elif user_role == 1:
        stages = list(user.stageparticipants_set.all())
    else:
        stages = list(user.stagestaff_set.all())
    return stages


def is_user_participates_in_stage(user: User, stage: Stage) -> bool:
    return len(StageParticipants.objects.filter(user=user, stage=stage)) != 0


def get_events_by_role(django_user: DjangoUser = None, user_role=0) -> Union[List, Union[Tuple, Event, Stage, int]]:
    """
    Получить список всех мероприятий по заданным параметрам
    :param django_user: Пользователь, сделавший запрос
    :param user_role: Роль пользователя. (0 - все, 1 - участник, 2 - модератор)
    :return: Список из троек: мероприятие, его первый этап, bool участвует ли django_user в этом мероприятии
    """

    user_events = set()
    if (not django_user.is_anonymous) and django_user is not None:
        user = get_user_by_django_user(django_user)
        user_events = get_user_events(user, user_role)

    result = list()
    for event in user_events:
        result.append((event, event.stage_set.first, True))
    return result


def get_user_by_django_user(django_user: DjangoUser) -> User:
    """

    :param dj_user: Пользователь в django-формате (обычно передаётся в качестве request.user)
    :return: User from user_handler

    """
    try:
        user = User.objects.get(user=django_user)
    except ObjectDoesNotExist:
        user = create_user_for_django_user(django_user=django_user)
    return user


def create_default_stage() -> Stage:
    stage = Stage()
    stage.save()
    return stage


def create_event(event: Event) -> None:
    Event.objects.create(event)


def get_event_by_id(id: int) -> Event:
    return Event.objects.get(id=id)


def get_stages_by_event(event: Event):
    return Stage.objects.filter(parent=event)


def get_open_stages_by_event(event: Event):
    waiting_status = Stage.Status.WAITING
    return Stage.objects.filter(parent=event, status=waiting_status, settings__can_register=True)


def get_event_by_stage(stage: Stage) -> Event:
    return stage.parent


def check_user_participate_in_stage(django_user: User, stage: Stage) -> bool:
    if stage in map(lambda stage_part: stage_part.stage, get_user_stages(get_user_by_django_user(django_user))):
        return True
    return False


def get_stage_by_id(stage_id: int):
    return Stage.objects.get(id=stage_id)
