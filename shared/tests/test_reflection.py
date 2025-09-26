from shared.reflection import get_subclasses, typename

# Добавил за компанию, а тесты ниже ИИ написал
class TestTypename:
	class Test: pass
	class_for_testing = Test
	expected_name = 'Test'

	def test_class(self):
		assert typename(self.class_for_testing) == self.expected_name

	def test_instance(self):
		assert typename(self.class_for_testing()) == self.expected_name

class TestGetSubclasses:
	def test_no_subclasses(self):
		"""Тест для класса без подклассов"""
		class Base: pass
		
		result = get_subclasses(Base)
		assert result == set()
	
	def test_single_level_inheritance(self):
		"""Тест для одноуровневого наследования"""
		class A: pass
		class B(A): pass
		class C(A): pass
		
		result = get_subclasses(A)
		assert result == {B, C}
	
	def test_multi_level_inheritance(self):
		"""Тест для многоуровневого наследования"""
		class A: pass
		class B(A): pass
		class C(B): pass
		class D(C): pass
		
		result = get_subclasses(A)
		assert result == {B, C, D}
	
	def test_multiple_inheritance(self):
		"""Тест для множественного наследования"""
		class A: pass
		class B: pass
		class C(A, B): pass
		class D(C): pass
		
		result_a = get_subclasses(A)
		result_b = get_subclasses(B)
		
		assert result_a == {C, D}
		assert result_b == {C, D}
	
	def test_complex_hierarchy(self):
		"""Тест для сложной иерархии классов"""
		class A: pass
		class B(A): pass
		class C(A): pass
		class D(B): pass
		class E(B, C): pass
		class F(D): pass
		class G(E): pass
		
		result = get_subclasses(A)
		assert result == {B, C, D, E, F, G}
	
	def test_diamond_inheritance(self):
		"""Тест для ромбовидного наследования"""
		class A: pass
		class B(A): pass
		class C(A): pass
		class D(B, C): pass
		
		result = get_subclasses(A)
		assert result == {B, C, D}
	
	def test_builtin_types(self):
		"""Тест со встроенными типами (должен работать, если есть подклассы)"""
		result = get_subclasses(Exception)
		# Должен вернуть непустое множество подклассов Exception
		assert isinstance(result, set)
		assert all(issubclass(cls, Exception) for cls in result)
	
	def test_return_type(self):
		"""Тест типа возвращаемого значения"""
		class A: pass
		class B(A): pass
		
		result = get_subclasses(A)
		assert isinstance(result, set)
		assert all(isinstance(cls, type) for cls in result)
