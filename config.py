import os.path

SECRET_KEY = 'chave_secreta_do_TI'
DEBUG = True
DB_HOST = 'localhost'
DB_NAME = r'C:\Users\Aluno\Desktop\Banco Caique\BANCO.FDB'
DB_USER = 'sysdba'
DB_PASSWORD = 'sysdba'


UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__))