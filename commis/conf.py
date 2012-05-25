import os

from django.conf import settings

COMMIS_TIME_SKEW = getattr(settings, 'COMMIS_TIME_SKEW', 15*60)

COMMIS_VALIDATOR_NAME = getattr(settings, 'COMMIS_VALIDATOR_NAME', 'chef-validator')

COMMIS_FILE_ROOT = getattr(settings, 'COMMIS_FILE_ROOT', os.path.join(settings.MEDIA_ROOT, 'sandbox'))
