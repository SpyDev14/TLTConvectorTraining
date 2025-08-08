from django.conf 	import settings
from django.db 		import models

from ckeditor.fields import RichTextField


class Article(models.Model):
	title = models.CharField(max_length = 128, verbose_name = "Заголовок")
	image = models.ImageField(upload_to = settings.IMAGES_ROOT/'articles')
	content = RichTextField(verbose_name = "Содержимое")
	created_at = models.DateTimeField(auto_now_add = True)

	class Meta:
		verbose_name = "Статья"
		verbose_name_plural = "Статьи"

	def __str__(self):
		return f"{self.title} от {self.created_at.strftime("%d/%m/%Y, %H:%M")}"
