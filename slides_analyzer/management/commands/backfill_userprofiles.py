from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from slides_analyzer.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile for users who do not have one (one-time backfill) and ensure all profiles are not deleted.'

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        undeleted_count = 0
        for user in users:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created UserProfile for user: {user.username}'))
            if profile.is_deleted:
                profile.is_deleted = False
                profile.save()
                undeleted_count += 1
                self.stdout.write(self.style.SUCCESS(f'Set is_deleted=False for user: {user.username}'))
        if created_count == 0:
            self.stdout.write(self.style.SUCCESS('All users already have a UserProfile.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created {created_count} UserProfile(s).'))
        if undeleted_count == 0:
            self.stdout.write(self.style.SUCCESS('No UserProfiles needed undeletion.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated {undeleted_count} UserProfile(s) to is_deleted=False.')) 