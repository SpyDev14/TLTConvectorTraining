from django.db 		import models

from phonenumber_field.modelfields 	import PhoneNumberField
from solo.models 					import SingletonModel


class SiteSettings(SingletonModel):
	site_favicon = models.ImageField(blank = True, upload_to = "favicon",
		verbose_name = "Favicon сайта")
	robots_txt_content = models.TextField(blank = True, verbose_name = "Содержимое Robots.txt")
	head_script = models.TextField(blank = True, verbose_name = "Добавить в <head>",
		help_text = "Этот текст будет вставлен в блок &ltscript&gt в <head> каждой html-странице сайта")
	
	class Meta:
		verbose_name = "Настройки сайта"
	def __str__(self): return ""


class CompanyContacts(SingletonModel):
	first_phone_number     = PhoneNumberField(blank = True, verbose_name = "Первый номер телефона")
	secondary_phone_number = PhoneNumberField(blank = True, verbose_name = "Второй номер телефона")
	email  = models.EmailField(blank = True, verbose_name = "Эл. почта")
	addres = models.CharField(max_length = 128, blank = True, verbose_name = "Адрес")
	work_time_text = models.CharField(max_length = 32, blank = True,
		verbose_name = "Время работы")

	class Meta:
		verbose_name = "Контакты компании"
	def __str__(self): return ""
