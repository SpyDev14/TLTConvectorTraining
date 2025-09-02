from logging import Filter
import re

from shared.string_processing.regex.patterns import TELEGRAM_BOT_TOKEN_PATTERN


class TelegramBotTokenFilter(Filter):
	PATTERN = re.compile(TELEGRAM_BOT_TOKEN_PATTERN)

	def hide_tokens(self, text: str):
		return self.PATTERN.sub('***TELEGRAM_BOT_TOKEN***', text)

	def filter(self, record):
		# Обрабатываем основное сообщение
		record.msg = self.hide_tokens(record.msg)

		# Обрабатываем аргументы форматирования
		if record.args:
			record.args = tuple(
				self.hide_tokens(arg) if isinstance(arg, str) else arg
				for arg in record.args
			)

		return True
