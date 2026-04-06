# Translations for English and Dari (Farsi)
TRANSLATIONS = {
	"en": {
		"language_label": "Select Language / زبان انتخاب کنید:",
		"chat_history": "Chat History",
		"new_chat": "+ New Chat",
		"new_chat_title": "New Chat",
		"clear_history": "Clear Current Chat",
		"example_prompts": "Example Prompts",
		"chatbot_description": "Learn programming and improve your employability skills with BanuCode",
		"user_input_placeholder": "Type your question here...",
		"please_wait": "Please wait while generating response...",
		"example_prompt_items": [
			"How do I build a Python learning roadmap?",
			"Explain object-oriented programming with a simple example.",
			"How can I improve my CV for junior developer roles?",
			"Give me a practical 2-week coding interview prep plan.",
		],
		"showing_latest": "Showing latest",
		"messages_suffix": "messages in this chat.",
	},
	"dari": {
		"language_label": "زبان را انتخاب کنید / Select Language:",
		"chat_history": "تاریخچه چت",
		"new_chat": "+ گفتگوی جدید",
		"new_chat_title": "گفتگوی جدید",
		"clear_history": "پاک کردن چت فعلی",
		"example_prompts": "نمونه سوالات",
		"chatbot_description": "با بانوکد برنامه نویسی را یاد بگیرید و مهارت های کاریابی خود را تقویت کنید",
		"user_input_placeholder": "سوال خود را اینجا بنویسید...",
		"please_wait": "لطفاً منتظر باشید...",
		"example_prompt_items": [
			"چگونه برای یادگیری پایتون یک نقشه راه بسازم؟",
			"برنامه نویسی شی گرا را با یک مثال ساده توضیح دهید.",
			"چگونه رزومه خود را برای شغل برنامه نویسی بهتر کنم؟",
			"یک برنامه عملی دو هفته ای برای آمادگی مصاحبه فنی بدهید.",
		],
		"showing_latest": "نمایش آخرین",
		"messages_suffix": "پیام های این چت.",
	},
}


def get_all_translations(language: str = "en") -> dict:
	"""Get all translations for a given language."""
	if language not in TRANSLATIONS:
		language = "en"
	return TRANSLATIONS[language]



