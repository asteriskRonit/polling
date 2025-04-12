from django.contrib import admin
from .models import CustomUser,Poll, PollOption

admin.site.register(CustomUser)
admin.site.register(Poll)
admin.site.register(PollOption)
