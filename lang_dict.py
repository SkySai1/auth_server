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
    },
    'fr': {
        'title': 'Connexion au système',
        'username_placeholder': 'Nom d’utilisateur',
        'password_placeholder': 'Mot de passe',
        'login_button': 'Se connecter',
        'error_message': "Nom d'utilisateur ou mot de passe invalide"
    },
    'de': {
        'title': 'Anmeldung im System',
        'username_placeholder': 'Benutzername',
        'password_placeholder': 'Passwort',
        'login_button': 'Einloggen',
        'error_message': 'Ungültiger Benutzername oder Passwort'
    },
    'es': {
        'title': 'Inicio de sesión en el sistema',
        'username_placeholder': 'Nombre de usuario',
        'password_placeholder': 'Contraseña',
        'login_button': 'Iniciar sesión',
        'error_message': 'Nombre de usuario o contraseña inválidos'
    },
    'it': {
        'title': 'Accesso al sistema',
        'username_placeholder': 'Nome utente',
        'password_placeholder': 'Password',
        'login_button': 'Accedi',
        'error_message': 'Nome utente o password non validi'
    },
    'zh': {
        'title': '登录系统',
        'username_placeholder': '用户名',
        'password_placeholder': '密码',
        'login_button': '登录',
        'error_message': '用户名或密码无效'
    }
}

def get_language(lang_code='en'):
    return LANGUAGES.get(lang_code, LANGUAGES['en'])
