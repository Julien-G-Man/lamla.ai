from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Update the Django site domain from example.com to the correct domain'

    def handle(self, *args, **options):
        try:
            # Get the site with ID 1 (default site)
            site = Site.objects.get(id=settings.SITE_ID)
            
            # Update the domain to your actual domain
            # Use the setting from Django settings
            new_domain = getattr(settings, 'SITE_DOMAIN', 'lamla-ai.onrender.com')
            new_name = 'LAMLA AI'
            
            if site.domain != new_domain:
                site.domain = new_domain
                site.name = new_name
                site.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully updated site domain from "{site.domain}" to "{new_domain}"'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Site domain is already set to "{new_domain}"'
                    )
                )
                
        except Site.DoesNotExist:
            # Create the site if it doesn't exist
            new_domain = getattr(settings, 'SITE_DOMAIN', 'lamla-ai.onrender.com')
            new_name = 'LAMLA AI'
            site = Site.objects.create(
                id=settings.SITE_ID,
                domain=new_domain,
                name=new_name
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created site with domain "{new_domain}"'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error updating site domain: {str(e)}'
                )
            ) 