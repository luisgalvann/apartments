from decouple import config


# Application paths
APT_VIEW_PATH = './apps/apartments/views/apartments_vi.ui'
FORM_VIEW_PATH = './apps/apartments/views/form_vi.ui'
CITY_FORM_VIEW_PATH = './apps/apartments/views/city_form_vi.ui'
EXPORTS_PATH = './common/resources/exports/'
DICTIONARY_PATH = 'sqlite:///common/resources/dbs/dictionary.db'
LOREM_PATH = './common/resources/texts/lorem_ipsum.txt'
QSS_STYLES_PATH = './common/resources/styles/'
ICONS_PATH = './common/resources/icons/'


# Environment variables
DB_DRIVER = config('DB_DRIVER')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT')
DB_NAME = config('DB_NAME')


# Main Connection String
CONN_STRING = f'{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
