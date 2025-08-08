from enum import StrEnum

# Я разместил это здесь потому, что вне зависимости от того, как и где
# мы работаем с Telegram API - эти значения не будут меняться.
class MessageParseMode(StrEnum):
	NONE = 'null'
	HTML = 'HTML'
	MARKDOWN = 'MarkdownV2'
