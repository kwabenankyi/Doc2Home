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
    MAIL_USERNAME = '' #replace with correct username and password for account
    MAIL_PASSWORD = ''
    ADMINS = [MAIL_USERNAME]
