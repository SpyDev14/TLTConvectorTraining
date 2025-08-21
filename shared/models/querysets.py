from django.db.models 	import QuerySet, Model


class IndividualizedBulkOperationsQuerySet(QuerySet):
	"""
	Заменяет массовые операции на индивидуальные операции с каждым
	элементом в QuerySet
	"""

	def update(self, **kwargs):
		"""
		Заменяет массовое обновление на индивидуальные обновления
		"""
		counter = 0

		obj: Model
		for obj in self:
			for key, value in kwargs.items():
				setattr(obj, key, value)
			obj.save()
			counter += 1
		return counter

	def delete(self):
		"""
		Заменяет массовое удаление на индивидуальные удаления
		"""
		counter = 0

		obj: Model
		for obj in self:
			obj.delete()
			counter += 1
		return counter

	def bulk_create(self, objs, *args, **kwargs):
		"""
		Заменяет массовое создание на индивидуальное сохранение
		"""
		created_objs = []

		obj: Model
		for obj in objs:
			obj.save()
			created_objs.append(obj)
		return created_objs
	
	def bulk_update(self, objs, fields, *args, **kwargs):
		"""
		Заменяет массовое обновление на индивидуальные сохранения
		Похоже на update(), но для уже загруженных объектов с разными значениями
		"""
		updated_count = 0

		obj: Model
		for obj in objs:
			obj.save(update_fields=fields)
			updated_count += 1
		return updated_count
