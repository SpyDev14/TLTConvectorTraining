from django.test import TestCase
from core.models import TelegramSendingChannel

# Я не буду писать тесты, но я хотел проверить именно это взаимодействие
# и вместо проверки в shell решил сделать вот так
class TelegramSendingChannelTest(TestCase):
	def test_get_by_specialization(self):
		specialization = TelegramSendingChannel.Specialization.LOGS
		channel = TelegramSendingChannel.get_by_specialization(specialization)

		self.assertIsNone(channel)
