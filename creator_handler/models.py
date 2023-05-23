from django.db import models


class StageSettings(models.Model):
    """
    Класс **StageSettings**

    Настройки стадии мероприятия

    :param can_user_choose_venue: Выбор площадки пользователем
    :param application_auto_accept: Автопринятие заявок
    :param public_participant_list: Публичный список участников
    :param contacts_is_visible: Отображение контактов
    :param who_can_edit_venues: Кто может радактировать площадки
    :param who_can_accept_applications: Кто может принимать заявки
    :param who_can_manage_mailing_list: Кто может управлять рассылкой

    """
    class AccessLevel(models.IntegerChoices):
        """
        Именованные константы для отображения уровня доступа к функциям настройки
        Можно расширить

        :param STAFF:
        :param CURATOR:
        :param PROVIDER:
        """
        STAFF = 5
        CURATOR = 10
        PROVIDER = 100

    can_register = models.BooleanField("Можно зарегистрироваться", default=False, null=False)
    can_user_choose_venue = models.BooleanField("Выбор площадки пользователем", default=False)
    application_auto_accept = models.BooleanField("Автопринятие заявок", default=False)
    public_participant_list = models.BooleanField("Публичный список участников", default=False)
    contacts_is_visible = models.BooleanField("Отображение контактов", default=False)
    who_can_edit_venues = models.SmallIntegerField("Кто может радактировать площадки", choices=AccessLevel.choices,
                                                   default=AccessLevel.PROVIDER)
    who_can_accept_applications = models.SmallIntegerField("Кто может принимать заявки", choices=AccessLevel.choices,
                                                           default=AccessLevel.PROVIDER)
    who_can_manage_mailing_list = models.SmallIntegerField("Кто может управлять рассылкой", choices=AccessLevel.choices,
                                                           default=AccessLevel.PROVIDER)
    contest_id = models.TextField("ID контеста", default="", null=True, blank=True)

    def __str__(self):
        try:
            return str(self.stage)
        except:
            return f"Настройки лежат сами по себе. {self.id}"

    class Meta:
        """
        Настройка отображения в админ-панели
        """
        verbose_name = 'Настройки этапа'
        verbose_name_plural = 'Настройки этапа'
