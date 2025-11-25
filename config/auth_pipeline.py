"""
Custom authentication pipeline functions for social auth
"""


def get_username(strategy, details, backend, user=None, *args, **kwargs):
    """
    Generate username from email address for Azure AD users.
    
    Azure AD provides email but not username, so we create one
    from the email address (part before @).
    
    If a user with that username already exists and has the same email,
    link to that existing user instead of creating a new one.
    """
    if not user:
        email = details.get('email')
        if email:
            # Use the part before @ as username
            username = email.split('@')[0]
            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Check if user exists with this username
            existing_user = User.objects.filter(username=username).first()
            
            # If exists and has same email (or no email set), use it
            if existing_user and (not existing_user.email or existing_user.email == email):
                # Update email if not set
                if not existing_user.email:
                    existing_user.email = email
                    existing_user.save()
                # Return the existing user to link the OAuth account
                return {'username': username, 'user': existing_user}
            
            # Otherwise, make username unique
            if existing_user:
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
            
            # Update the details dict directly so it's passed to create_user
            details['username'] = username
    
    return {'username': details.get('username')}
