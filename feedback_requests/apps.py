from django.apps import AppConfig


class FeedbackRequestsConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'feedback_requests'
	verbose_name = 'Заявки'

	def ready(self):
		from . import signals
