from django.conf 	import settings
from django.db 		import models

from phonenumber_field.modelfields 	import PhoneNumberField
from solo.models 					import SingletonModel


# MARK: Singleton models
class SiteSettings(SingletonModel):
	site_favicon       = models.ImageField(blank = True, upload_to = settings.MEDIA_ROOT / "icons",
		verbose_name = "Favicon сайта")
	robots_txt_content = models.TextField(blank = True, verbose_name = "Содержимое Robots.txt")
	html_head_addition = models.TextField(blank = True, verbose_name = "Добавить в <head>",
		help_text = "Этот текст будет вставлен в конец в указанного тега на каждой html странице сайта")
	
	class Meta:
		verbose_name = "Настройки сайта"
	def __str__(self): return "Настройки сайта"


class CompanyContacts(SingletonModel):
	tg_contact_link = models.URLField(blank = True, verbose_name = "Telegram")
	vk_contact_link = models.URLField(blank = True, verbose_name = "Вконтакте")
	phone_number    = PhoneNumberField(blank = True, verbose_name = "Номер телефона")
	email  = models.EmailField(blank = True, verbose_name = "E-mail")
	addres = models.CharField(max_length = 128, blank = True, verbose_name = "Адрес")

	class Meta:
		verbose_name = "Контакты"
	def __str__(self): return "Контакты"


# MARK: Regular models
class Page(models.Model):
	title = models.CharField(max_length = 32, verbose_name = "HTML Title")
	description = models.CharField(max_length = 32, verbose_name = "HTML Description")
	# ...

	class Meta:
		verbose_name = "Страница"
		verbose_name_plural = "Страницы"
	def __str__(self): return "Страница"


class FeedbackRequest(models.Model):
	requestener_name = models.CharField(max_length = 24, verbose_name = "Имя")
	phone_number     = PhoneNumberField(verbose_name = "Номер телефона")
	comment          = models.TextField(max_length = 2048, verbose_name = "Комментарий")
	created_at       = models.DateTimeField(auto_now_add = True, verbose_name = "Дата заполнения заявки")

	class Meta:
		verbose_name = 'Заявка на обратную связь'
		verbose_name_plural = 'Заявки на обратную связь'
		# app_label = 'Заявки'
		# https://chat.deepseek.com/a/chat/s/9f85ac4a-9cd4-4dc4-bb04-209d7db3c4af

	def __str__(self):
		return f'{self.requestener_name} {self.phone_number}'
