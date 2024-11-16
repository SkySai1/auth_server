# lang_dict.py
LANGUAGES = {
    'en': {
        'title': 'Login to the system',
        'username_placeholder': 'Username',
        'password_placeholder': 'Password',
        'login_button': 'Login',
        'error_message': 'Invalid username or password'
    },
    'redneck_us': {
        'title': 'Y’all, log on in!',
        'username_placeholder': 'Whatcha go by?',
        'password_placeholder': 'Secret pass',
        'login_button': 'Git ‘er done!',
        'error_message': 'Dang it, wrong name or pass. Try agin, buddy.'
    },
    'irish_gang': {
        'title': 'Login, ya lad!',
        'username_placeholder': 'What’s yer name, mate?',
        'password_placeholder': 'Yer code, quick!',
        'login_button': 'Get inside, quick!',
        'error_message': 'Oi! Wrong name or code. Try it again, mate.'
    },
    'ru': {
        'title': 'Вход в систему',
        'username_placeholder': 'Имя пользователя',
        'password_placeholder': 'Пароль',
        'login_button': 'Войти',
        'error_message': 'Неверные учетные данные. Пожалуйста, попробуйте снова.'
    },
    'imperial_ru': {
        'title': 'Вход в систему',
        'username_placeholder': 'Ваше имя',
        'password_placeholder': 'Ваш пароль',
        'login_button': 'Входить',
        'error_message': 'Неверные данные для входа. Попробуйте вновь.'
    },
    'soviet_ru': {
        'title': 'Вход в систему, товарищ!',
        'username_placeholder': 'Товарищ, введите имя',
        'password_placeholder': 'Пароль (секретный)',
        'login_button': 'Войти в систему',
        'error_message': 'Товарищ, неверные учетные данные! Попробуйте еще раз.'
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
