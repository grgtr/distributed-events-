from django.db import models
from user_handler.models import User
from creator_handler.models import StageSettings

class Event(models.Model):
    """
    Класс **Event**

    Мероприятие и его описание

    :param name: название мероприятия
    :param description: информация о мероприятии

    """

    name = models.CharField("Название мероприятия", default="Новое мероприятие", max_length=50)
    description = models.TextField(null=True, blank=True, max_length=500)

    def __str__(self):
        return self.name

    class Meta:
        """
        Настройка отображения в админпанели
        """
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
        ordering = ['name']





class Stage(models.Model):
    """
    Класс **Stage**

    Этап и информация о нём

    :param name: название этапа
    :param description: описание этапа
    :param parent: родитель
    :param preview: превью
    :param users: участники
    :param status: статус
    :param time_start: начало
    :param time_end: конец
    :param contacts: Контакты

    """
    class Status(models.IntegerChoices):
        """
        Именованные константы, отображающие статус этапа мероприятия
        Можно расширить

        :param WAITING:
        :param ACTIVE:
        :param ENDED:

        """
        WAITING = 0
        ACTIVE = 1
        ENDED = 2

    name = models.CharField("Название этапа", default="Новый этап", max_length=50)
    parent = models.ForeignKey(Event, on_delete=models.CASCADE)

    contacts = models.TextField(null=True, blank=True, max_length=100)
    description = models.TextField(null=True, blank=True, max_length=500)
    preview = models.TextField(null=True, blank=True, max_length=100)

    users = models.ManyToManyField(User, through="StageParticipants", related_name="users")
    staff = models.ManyToManyField(User, through="StageStaff", related_name="staff")
    status = models.SmallIntegerField(null=True, default=Status.WAITING, choices=Status.choices)

    settings = models.OneToOneField(StageSettings, default=StageSettings, null=True, on_delete=models.CASCADE)
    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)
    next_stage = models.ForeignKey("self", null=True, on_delete=models.DO_NOTHING, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        """
        Настройка отображения в админ-панели
        """
        verbose_name = 'Этап'
        verbose_name_plural = 'Этапы'
        ordering = ['name']

class Venue(models.Model):
    """
    Класс **Venue**

    Площадка и информация о ней

    :param name: название этапа
    :param address: адрес проведения
    :param region: Регион, в котором площадка
    :param participants_maximum: Максимальное число участников
    :param parental_stage: Stage, на котором проводится мероприятие
    :param contacts: Контакты

    """
    name = models.CharField("Название", max_length=50)
    address = models.TextField("Адрес", max_length=500)
    region = models.SmallIntegerField("Регион, в котором площадка", null=True, blank=True)
    participants_maximum = models.IntegerField("Максимальное число участников", null=True, blank=True)
    parental_stage = models.ForeignKey(Stage, null=True, on_delete=models.SET_NULL)
    contacts = models.TextField("Контакты", max_length=100, null=True, blank=True)

    #parental_event = models.ForeignKey(Event, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        """
        Настройка отображения в админ-панели
        """
        verbose_name = 'Площадка проведения'
        verbose_name_plural = 'Площадки проведения'
        ordering = ['name']


class StageParticipants(models.Model):
    """
    Класс **StageParticipants**

    :param stage: Стадия
    :param user: User
    :param status: статус
    :param venue: Место проведения
    :param role: Роль
    :param score: Баллы

    """
    class Status(models.IntegerChoices):
        """
        Именованные константы для отображения статуса заявки(участия) в мероприятии
        Можно расширить

        :param AWAITED:
        :param ACCEPTED:
        :param REJECTED:
        :param BANNED:

        """
        AWAITED = 0
        ACCEPTED = 200
        REJECTED = 400
        BANNED = 404

    class Roles(models.IntegerChoices):
        """
        Именованные константы для отображеня роли учатися в мероприятии
        Можно расширить

        :param PARTICIPANT:
        :param AWARDEE:
        :param WINNER:

        """
        PARTICIPANT = 0
        AWARDEE = 10
        WINNER = 100

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True)
    role = models.SmallIntegerField("Роль", choices=Roles.choices, default=Roles.PARTICIPANT)
    status = models.SmallIntegerField("Статус заявки", choices=Status.choices, default=Status.AWAITED)
    score = models.SmallIntegerField("Количество баллов", null=True, default=0)
    yandex_contest_id = models.CharField("Id в Яндекс.Контесте", blank=True, max_length=50)

    class Meta:
        """
        Настройка отображения в админ-панели
        """
        verbose_name = 'Участники этапов'
        verbose_name_plural = 'Участники этапов'


class StageStaff(models.Model):
    """
    Класс **StageStaff**

    :param stage: Стадия
    :param user: User
    :param status: статус
    :param venue: Место проведения
    :param role: Роль

    """
    class Status(models.IntegerChoices):
        """
        Именованные константы, обозначающие статус работника на площадке

        :param ACCEPTED:
        :param FIRED:
        :param WAITING:

        """
        ACCEPTED = 200
        FIRED = 400
        WAITING = 0

    class Roles(models.IntegerChoices):
        """
        Именованные константы, обозначающие роли работников на площадках

        :param STAFF:
        :param CURATOR:
        :param PROVIDER:

        """
        STAFF = 5
        CURATOR = 10
        PROVIDER = 100

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True)
    role = models.SmallIntegerField("Роль", choices=Roles.choices, default=Roles.STAFF)
    status = models.SmallIntegerField("Статус", choices=Status.choices, default=Status.WAITING)

    class Meta:
        """
        Настройка отображения в админ-панели
        """
        verbose_name = 'Модераторы этапов'
        verbose_name_plural = 'Модераторы этапов'


class StageRelation(models.Model):
    stage_from = models.OneToOneField(Stage, related_name="stage_from", on_delete=models.CASCADE)
    stage_to = models.OneToOneField(Stage, related_name="stage_to", on_delete=models.CASCADE)
