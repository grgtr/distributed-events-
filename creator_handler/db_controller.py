from event_handler.models import Event, Stage, StageStaff, StageParticipants, Venue
from creator_handler.models import StageSettings
from user_handler.models import DjangoUser, User

from django.core.exceptions import ObjectDoesNotExist
from enum import Enum
from typing import Union, List, Tuple, Set

from event_handler.db_controller import get_user_by_django_user, get_stages_by_event, get_event_by_id, \
    get_event_by_stage, get_stage_by_id

import creator_handler.contest_controller as contest


def get_participants_by_event(event: Event):
    stages = get_stages_by_event(event)
    stage_ids = [stage.id for stage in stages]
    stage_participants = StageParticipants.objects.filter(stage__in=stage_ids)
    return stage_participants


def get_staff_by_event(event: Event):
    stage = get_stages_by_event(event).first()
    return [] if stage.users is None else stage.users


class SettingsSet(Enum):
    EDIT_VENUES = 1
    ACCEPT_APPLICATIONS = 2
    MANAGE_MAILING_LIST = 3


def get_venues_by_event(event_id: int):
    return Venue.objects.filter(parental_event_id=event_id)


def get_venues_by_stage_id(stage_id: int):
    return Venue.objects.filter(parental_stage_id=stage_id)


def get_venue_by_id(venue_id: int):
    return Venue.objects.get(id=venue_id)


def get_venue_by_id_dict(venue_id: int):
    try:
        venue = get_venue_by_id(venue_id)
    except ObjectDoesNotExist:
        venue = {}
    except Exception as e:
        print(e)
        venue = {}
    return venue


def user_have_access(django_user: DjangoUser, event_id: int, setting=-1) -> bool:
    user = get_user_by_django_user(django_user)
    # print(user)
    try:
        stage = get_stages_by_event(get_event_by_id(event_id)).filter(next_stage__isnull=True).first()
        staff = StageStaff.objects.get(user=user, stage=stage)
        setting_rule = 0
        if setting == SettingsSet.EDIT_VENUES:
            setting_rule = stage.settings.who_can_edit_venues
        elif setting == SettingsSet.ACCEPT_APPLICATIONS:
            setting_rule = stage.settings.who_can_accept_applications
        elif setting == SettingsSet.MANAGE_MAILING_LIST:
            setting_rule = stage.settings.who_can_manage_mailing_list
        return staff.status == StageStaff.Status.ACCEPTED and staff.role >= setting_rule
    except ObjectDoesNotExist:
        return False


def create_venue(name: str, address: str, region: int, participants_maximum: int, contacts: str, stage_id: int) -> None:
    try:
        Venue.objects.create(
            name=name,
            address=address,
            region=region,
            participants_maximum=participants_maximum,
            parental_stage=get_stage_by_id(stage_id),
            contacts=contacts,
        )
    except Exception as e:
        print(e)


def edit_venue(name: str, address: str, region: int, participants_maximum: int, contacts: str, venue_id: int) -> None:
    try:
        venue = Venue.objects.filter(id=venue_id).update(
            name=name,
            address=address,
            region=region,
            participants_maximum=participants_maximum,
            contacts=contacts,
        )
    except Exception as e:
        print(e)


def is_venue_attached_to_event(event_id: int, venue_id: int) -> bool:
    try:
        venue = get_venue_by_id(venue_id)
        event_stages = get_stages_by_event(get_event_by_id(event_id))
        # print(event_stages, "//", venue, "//",venue.parental_stage, "//", event_id)
        is_attached = False
        for stage in event_stages:
            if stage == venue.parental_stage:
                is_attached = True
                break
        return is_attached
    except ObjectDoesNotExist:
        return False


def register_on_stage(stage_id: int, venue_id: int, user: User):
    stage = get_stage_by_id(stage_id)
    venue = get_venue_by_id(venue_id)
    if not is_venue_attached_to_event(get_event_by_stage(stage).id, venue_id):
        raise ValueError
    participation = StageParticipants.objects.get_or_create(stage=stage, user=user)[0]
    participation.role = StageParticipants.Roles.PARTICIPANT
    participation.status = StageParticipants.Status.ACCEPTED
    participation.venue = venue
    participation.save()


def make_record_event(name, description):
    event = Event.objects.create(name=name, description=description)
    return event


def make_record_stage(name, event, preview="Пустое превью", time_start=None,
                      time_end=None, description="пустое описание", next_stage=None):
    stage = Stage.objects.create(
        name=name,
        parent=event,
        preview=preview,
        time_start=time_start,
        time_end=time_end,
        description=description,
        settings=StageSettings.objects.create(),
        next_stage=next_stage,
    )
    return stage


def get_stage_subtree(stage: int, to_delete):
    previous_stages = Stage.objects.filter(next_stage=stage).values_list('id', flat=True)
    for previous_stage in previous_stages:
        get_stage_subtree(previous_stage, to_delete)
    to_delete.append(stage)


def delete_stage_recursive(stage: int):
    to_delete = []
    get_stage_subtree(stage, to_delete)
    # print(to_delete)
    Stage.objects.filter(id__in=to_delete).delete()


def create_staff(user, stage, role, status=Stage.Status.WAITING):
    StageStaff.objects.create(user=user,
                              stage=stage,
                              role=role,
                              status=status)


def reject_participant(user: User, event_id: int):
    try:
        stage = get_stages_by_event(get_event_by_id(event_id)).first()
        StageParticipants.objects.filter(user=user, stage=stage).update(status=StageParticipants.Status.REJECTED)
        return True
    except ObjectDoesNotExist:
        return False


def accept_participant(user: User, event_id: int):
    try:
        stage = get_stages_by_event(get_event_by_id(event_id)).first()
        StageParticipants.objects.filter(user=user, stage=stage).update(status=StageParticipants.Status.ACCEPTED)
        return True
    except ObjectDoesNotExist:
        return False


def ban_participant(user: User, event_id: int):
    try:
        stage = get_stages_by_event(get_event_by_id(event_id)).first()
        StageParticipants.objects.filter(user=user, stage=stage).update(status=StageParticipants.Status.BANNED)
        return True
    except ObjectDoesNotExist:
        return False


def get_event_partcipants(event_id: int):
    stage = get_stages_by_event(get_event_by_id(event_id)).first()
    return StageParticipants.objects.filter(stage=stage)


def get_formatted_stages(event_id: int):
    stages = get_stages_by_event(get_event_by_id(event_id))
    answer = []
    adjacency_list = {}
    final = -1
    fictive_stage = Stage(id=-1, name="fictive")
    stages_by_id = {-1: fictive_stage}
    for stage in stages:
        adjacency_list.setdefault(stage.id, []).append(fictive_stage.id)
    for stage in stages:
        stages_by_id[stage.id] = stage
        if stage.next_stage is not None:
            adjacency_list.setdefault(stage.next_stage.id, []).append(stage.id)
        else:
            final = stage.id
    if final == -1:
        raise ValueError
    for previous_stages in adjacency_list:
        adjacency_list[previous_stages].reverse()
    euler_bypass(final, adjacency_list, 0, answer, stages_by_id)
    return answer


def euler_bypass(stage_id: int, adjacency_list, depth: int, answer, stages_by_id):
    answer.append((stages_by_id[stage_id], depth))
    for previous_stage in adjacency_list.setdefault(stage_id, []):
        euler_bypass(previous_stage, adjacency_list, depth + 1, answer, stages_by_id)


def update_stage(stage_id: int, name, description, contacts, can_register):
    stage = get_stage_by_id(stage_id)
    stage.name = name
    stage.description = description
    stage.contacts = contacts
    stage.settings.can_register = can_register
    stage.save()
    stage.settings.save()


def change_role_of_participation(yandex_contest_ids: Union[
    List, str]) -> None:
    StageParticipants.objects.filter(yandex_contest_id__in=yandex_contest_ids, status=200).update(
        role=StageParticipants.Roles.AWARDEE)


def transfer_participants_to_next_stage(stage_id: int, venue_id: int = -1) -> None:
    stage = get_stage_by_id(stage_id)
    next_stage = stage.next_stage

    if venue_id == -1:
        venues = Venue.objects.filter(parental_stage_id=next_stage.id)

        if len(venues) == 0:
            create_venue("Площадка для Яндекс.Контеста", "Яндекс.Контест", None, None, None, next_stage.id)
            venues = Venue.objects.filter(parental_stage_id=next_stage.id)

        venue_id = venues[0].id

    awardees = StageParticipants.objects.filter(stage=stage, status=200, role__in=[StageParticipants.Roles.AWARDEE,
                                                                                   StageParticipants.Roles.WINNER])
    for awardee in awardees:
        register_on_stage(next_stage.id, venue_id, awardee.user)


def init_participants_id(stage):
    if not stage.settings.contest_id:
        return
    participants = StageParticipants.objects.filter(stage=stage)
    email_to_participant = dict()
    for participant in participants:
        email_to_participant[participant.user.user.email] = participant
    contest_participants = contest.get_participants(stage.settings.contest_id)
    for participant in contest_participants:
        participant = participant['participantInfo']
        try:
            email_to_participant[participant["login"]].yandex_contest_id = participant["id"]
            email_to_participant[participant["login"]].save()
        except Exception as e:
            print(e, f"User: {participant['login']}")


def end_stage(stage, end_score):
    if not stage.settings.contest_id:
        print("No contest")
        return
    init_participants_id(stage)
    contest_id = stage.settings.contest_id
    score_board = contest.get_standings(contest_id)

    participants = StageParticipants.objects.filter(stage=stage)
    id_to_paticipants = dict()
    for participant in participants:
        id_to_paticipants[participant.yandex_contest_id] = participant
    for score in score_board:
        info = score['participantInfo']
        score = score['score']
        try:
            id_to_paticipants[str(info['id'])].score = int(score)
            if (int(score)) >= end_score:
                id_to_paticipants[str(info['id'])].role = StageParticipants.Roles.AWARDEE
            id_to_paticipants[str(info['id'])].save()
        except Exception as e:
            print(e, info)

    if not stage.next_stage:
        return
    transfer_participants_to_next_stage(stage.id)
    awardees = StageParticipants.objects.filter(stage=stage,
                                                status=200, role__in=[StageParticipants.Roles.AWARDEE,
                                                                      StageParticipants.Roles.WINNER])

    login_list = list()
    for awardee in awardees:
        login_list.append(awardee.user.user.email)
    contest.register_participants(stage.next_stage.settings.contest_id, login_list)
