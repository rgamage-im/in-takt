"""
Custom authentication pipeline functions for social auth
"""


def get_username(strategy, details, backend, user=None, *args, **kwargs):
    """
    Generate username from email address for Azure AD users.
    
    Azure AD provides email but not username, so we create one
    from the email address (part before @).
    """
    if not user:
        email = details.get('email')
        if email:
            # Use the part before @ as username
            username = email.split('@')[0]
            
            # Make sure username is unique
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Update the details dict directly so it's passed to create_user
            details['username'] = username
    
    return {'username': details.get('username')}
