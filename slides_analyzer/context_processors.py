from .models import UserProfile

def user_profile(request):
    """
    Context processor to make user profile available in all templates
    """
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(user=request.user)
        return {'user_profile': profile}
    return {'user_profile': None}