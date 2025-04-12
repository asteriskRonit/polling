from rest_framework_simplejwt.tokens import AccessToken

def get_access_token_for_user(user):
    access = AccessToken.for_user(user)
    access['email'] = user.email
    return str(access)
