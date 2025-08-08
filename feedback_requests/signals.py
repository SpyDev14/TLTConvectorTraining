from django.db.models.signals 	import post_save
from django.dispatch 			import receiver

from core.models.general 	import TelegramSendingChannel
from feedback_requests.models 		import FeedbackRequest


@receiver(post_save, sender = FeedbackRequest)
def send_new_request_notification_into_telegram(sender, instance: FeedbackRequest, created, **kwargs):
	if not created:
		return

	telegram_sending_channel = TelegramSendingChannel.objects.get()
