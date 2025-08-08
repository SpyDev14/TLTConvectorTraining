# Я решил не создавать отдельную папку т.к тут будет максимум 1-2 модели, не более.
from django.db import models

from phonenumber_field.modelfields 	import PhoneNumberField


class FeedbackRequest(models.Model):
	requestener_name = models.CharField(max_length = 24, verbose_name = "Имя")
	phone_number     = PhoneNumberField(verbose_name = "Номер телефона")
	created_at       = models.DateTimeField(auto_now_add = True, verbose_name = "Дата заполнения заявки")

	class Meta:
		verbose_name = 'Заявка на обратную связь'
		verbose_name_plural = 'Заявки на обратную связь'

	def __str__(self):
		return f'Заявка от {self.requestener_name} {self.phone_number}'
