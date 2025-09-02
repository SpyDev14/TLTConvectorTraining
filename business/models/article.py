from django.conf 	import settings
from django.urls 	import reverse
from django.db 		import models

from ckeditor.fields import RichTextField
from tinymce.models import HTMLField

from core.models.bases import BaseRenderableModel


class ArticleManager(models.Manager):
	def ceo_ordered(self):
		return self.order_by('-created_at')

class Article(BaseRenderableModel):
	image = models.ImageField(upload_to = settings.IMAGES_ROOT/'articles')
	content = HTMLField("Содержимое")
	created_at = models.DateTimeField(auto_now_add = True)

	objects: ArticleManager = ArticleManager()

	class Meta:
		verbose_name = "Статья"
		verbose_name_plural = "Статьи"

	def __str__(self):
		return f"{self.name} от {self.created_at.strftime("%d/%m/%Y, %H:%M")}"
