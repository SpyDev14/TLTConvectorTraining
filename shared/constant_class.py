# INFO: Это работает, но я пока отложу это (писал ИИ)
# Отложу потому, что:
# 1. Не самый удобный и понятный всем API:
# class CONSTANTS(metaclass=ConstMeta): ...
# 2. Подклассы не наследуют логику:
# class CONSTANTS(metaclass=ConstMeta):
# 	class SUBCLASS: ... # Будет работать как обычный класс
# 3. Самое главное - это очень сложно выглядит, ничего не понятно.


# # Вариант 1
# class ConstMeta(type):
# 	"""Запрещает изменять класс и создавать его экземпляры,
# 	если параметр изменяемого типа - возвращает копию."""
# 	_FROZEN_FLAG = "__const_frozen"

# 	def __init__(cls, name, bases, attrs):
# 		super().__init__(name, bases, attrs)
# 		# # Замораживаем класс после создания
# 		setattr(cls, ConstMeta._FROZEN_FLAG, True)

# 	def __setattr__(cls, name: str, value):
# 		if getattr(cls, ConstMeta._FROZEN_FLAG, False):
# 			# # Разрешаем доступ к служебным атрибутам метакласса
# 			if name.startswith(f"_{cls.__name__}__") or name == ConstMeta._FROZEN_FLAG:
# 				return super().__setattr__(name, value)
# 			raise AttributeError(f"Class '{cls.__name__}' is immutable. Cannot set attribute '{name}'")
		
# 	def __delattr__(cls, name):
# 		if getattr(cls, ConstMeta._FROZEN_FLAG, False):
# 			raise AttributeError(f"Class '{cls.__name__}' is immutable. Cannot delete attribute '{name}'")
# 		super().__delattr__(name)

# 	def __call__(cls, *args, **kwargs):
# 		raise TypeError(f"Class '{cls.__name__}' is not instantiable")


# class ConstantClass(metaclass = ConstMeta):
# 	pass


# # Вариант 2
# import copy
# import types

# class ConstantMeta(type):
# 	def __new__(mcs, name, bases, cls_dict):
# 		# # Обрабатываем вложенные классы (кроме встроенных)
# 		new_dict = {}
# 		for attr_name, attr_value in cls_dict.items():
# 			if (isinstance(attr_value, type) and 
# 				not isinstance(attr_value, ConstantMeta) and
# 				attr_value.__module__ != 'builtins'):
# 				# # Рекурсивно применяем метакласс к вложенным классам
# 				new_dict[attr_name] = ConstantMeta(
# 					attr_value.__name__,
# 					attr_value.__bases__,
# 					dict(attr_value.__dict__)
# 				)
# 			else:
# 				new_dict[attr_name] = attr_value
		
# 		# # Создаем класс с защитой от изменений
# 		cls = super().__new__(mcs, name, bases, new_dict)
# 		return cls

# 	def __setattr__(cls, name, value):
# 		raise AttributeError(f"Cannot modify attribute '{name}' in constant class {cls.__name__}")

# 	def __delattr__(cls, name):
# 		raise AttributeError(f"Cannot delete attribute '{name}' in constant class {cls.__name__}")

# 	def __call__(cls, *args, **kwargs):
# 		raise TypeError(f"Cannot instantiate constant class {cls.__name__}")

# 	def __getattribute__(cls, name):
# 		# # Получаем атрибут обычным способом
# 		value = super().__getattribute__(name)
		
# 		# # Для классов и модулей возвращаем оригинал
# 		if isinstance(value, (type, types.ModuleType)):
# 			return value
			
# 		# # Для всех остальных - возвращаем глубокую копию
# 		return copy.deepcopy(value)

# def constantclass(cls):
# 	"""Декоратор для преобразования класса в неизменяемый контейнер констант"""
# 	return ConstantMeta(cls.__name__, cls.__bases__, dict(cls.__dict__))
