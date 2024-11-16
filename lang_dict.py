# lang_dict.py
LANGUAGES = {
    'en': {
        'title': 'Login to the system',
        'username_placeholder': 'Username',
        'password_placeholder': 'Password',
        'login_button': 'Login',
        'error_message': 'Invalid username or password'
    },
    'ru': {
        'title': 'Вход в систему',
        'username_placeholder': 'Имя пользователя',
        'password_placeholder': 'Пароль',
        'login_button': 'Войти',
        'error_message': 'Неверные учетные данные. Пожалуйста, попробуйте снова.'
    }
}

def get_language(lang_code='en'):
    return LANGUAGES.get(lang_code, LANGUAGES['en'])
