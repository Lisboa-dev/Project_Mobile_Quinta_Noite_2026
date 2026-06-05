from ..infra.repository.PostgresBellNotificationRepository import PostgresBellNotificationRepository
from .UserBellService import (
    CountUnreadNotificationsService,
    CreateNotificationService,
    ListUserNotificationsService,
    MarkAllNotificationsAsReadService,
    MarkNotificationAsReadService,
)


class UserBellContext:
    repository = PostgresBellNotificationRepository()

    @staticmethod
    def create_notification_service():
        return CreateNotificationService(UserBellContext.repository)

    @staticmethod
    def list_user_notifications_service():
        return ListUserNotificationsService(UserBellContext.repository)

    @staticmethod
    def count_unread_notifications_service():
        return CountUnreadNotificationsService(UserBellContext.repository)

    @staticmethod
    def mark_notification_as_read_service():
        return MarkNotificationAsReadService(UserBellContext.repository)

    @staticmethod
    def mark_all_notifications_as_read_service():
        return MarkAllNotificationsAsReadService(UserBellContext.repository)
