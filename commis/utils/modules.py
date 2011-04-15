import types

from django.conf import settings

def guess_app(obj):
    if isinstance(obj, types.ModuleType):
        name = obj.__name__
    elif isinstance(obj, basestring):
        name = obj
    else:
        name = obj.__module__
    possibles = []
    for app in settings.INSTALLED_APPS:
        if name.startswith(app):
            possibles.append(app)
    return max(possibles, key=len)

def guess_app_label(obj):
    app = guess_app(obj)
    if app is not None:
        return app.rsplit('.', 1)[-1]
