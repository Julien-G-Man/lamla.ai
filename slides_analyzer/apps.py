from django.apps import AppConfig


class SlidesAnalyzerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'slides_analyzer'
    
    def ready(self):
        import slides_analyzer.signals
