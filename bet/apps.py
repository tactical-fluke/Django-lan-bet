from django.apps import AppConfig

class BetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bet'

    def ready(self):
        from .wager_close_time_manager import wager_close_manager
        from threading import Thread
        thread = Thread(target=wager_close_manager, args=(30, ))
        thread.daemon = True
        thread.start()
