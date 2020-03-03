from os.path import join

FILES_ROOT_DIR = '/var/www/html/medibot_pythonbackend'
EMOTION_BASE_DIR = '/var/www/html/emotion_imgs'

DBPATH = join(FILES_ROOT_DIR,'db/')
DBNAME = 'user_states.db'

BASE_DOMAIN = 'https://cstenkamp.xyz/'
IMAGE_DOMAIN = join(BASE_DOMAIN, 'emotion_imgs')
BOT_DOMAIN = join(BASE_DOMAIN, 'medibot/')
MP3_ROOT_DOMAIN = join(BASE_DOMAIN, 'meditation_files')