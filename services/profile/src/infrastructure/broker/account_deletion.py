import logging

from infrastructure.broker.rabbitmq import broker
from domain.events import AccountDeletionNotification
from infrastructure.db.db_helper import db_helper
from domain.services.factory import create_profile_service


logger = logging.getLogger(__name__)


@broker.subscriber("account_deletion_queue")
async def handle_account_deletion(message: AccountDeletionNotification) -> None:
    async with db_helper.session_factory() as session:
        service = create_profile_service(session=session)
        deleted = await service.delete_account_data(user_id=message.user_id)

    if deleted:
        logger.info("Deleted profile data for user_id=%s", message.user_id)
    else:
        logger.info("No profile found for user_id=%s; nothing to delete", message.user_id)