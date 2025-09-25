from django.utils.safestring 	import mark_safe
from django.conf 				import settings
from django.db 					import models

from phonenumber_field.modelfields 	import PhoneNumberField
from solo.models 					import SingletonModel
from shared.models.validators 		import map_coordinates_format


class SiteSettings(SingletonModel):
	site_name = models.CharField('Название сайта', max_length=128, default="JBrony Site",
		help_text="В основном используется в base.html")
	favicon = models.ImageField(blank = True, upload_to = 'favicon')
	robots_txt_content = models.TextField('Содержимое Robots.txt', blank = True)
	head_script = models.TextField('Скрипт', blank = True,
		help_text = 'Этот текст будет вставлен в блок &ltscript&gt в &lthead&gt каждой html-страницы сайта')

	class Meta:
		verbose_name = '⚙ | Настройки сайта'
	def __str__(self): return '⚙ | Настройки сайта'


class CompanyInfo(SingletonModel):
	# Решил не делать отдельную модель для этого, это было бы избыточно
	first_phone_number     = PhoneNumberField('Первый номер телефона', blank = True)
	secondary_phone_number = PhoneNumberField('Второй номер телефона', blank = True)
	email  = models.EmailField('Эл. почта', blank = True)
	addres = models.CharField('Адрес', max_length = 128, blank = True)
	work_time_text = models.CharField('Время работы', max_length = 32, blank = True)
	map_coordinates = models.CharField('Координаты на карте', max_length = 32, blank = True,
		validators = [map_coordinates_format],
		help_text = mark_safe('Формат: <code>53.556350, 49.216210</code>'))

	class Meta:
		verbose_name = '📠 | Контакты компании'
	def __str__(self): return '📠 | Контакты компании'
