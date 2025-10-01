# Это находится здесь потому, что OgType и в африке OgType, оно никак не зависит от проекта
from enum import StrEnum

# Использую явные строки вместо auto() для надёжности
class OgType(StrEnum):		# Предназначения:
	ARTICLE = "article" 	# - Статьи, блог-посты, новости
	PRODUCT = "product" 	# - Товары в интернет-магазине
	PROFILE = "profile" 	# - Профили пользователей
	WEBSITE = "website" 	# - Главная страница, лендинги
	PLACE 	= "place" 		# - Места, локации
	BOOK 	= "book" 		# - Книги, литературные произведения
