import os
basedir = os.path.abspath(os.path.dirname(__file__))

#allows the object to communicate over webpage and link to db
class Config(object):#these are all the parameters passed through the venv: "set CONSTANT=whatever"
    SECRET_KEY = os.environ.get('SECRET_KEY') or "unguessable_secret_key"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir,'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = int(587)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'noreply.kwanea1@Gmail.com'
    MAIL_PASSWORD = 'wnxkdiejrtpkhlot'
    ADMINS = ['noreply.kwanea1@gmail.com']