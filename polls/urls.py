from django.urls import path
from .views import RegisterView,LoginView,CreatePollView,VoteCreateView,MyPollsView,PollUpdateAPIView
urlpatterns = [
    path('api/register', RegisterView.as_view(), name='register'),
    path('api/login', LoginView.as_view(), name='login'),
    path('api/create', CreatePollView.as_view(), name='create_poll'),
    path('api/vote', VoteCreateView.as_view(), name='vote'),
    path('api/data', MyPollsView.as_view(), name='my-polls'),
    path('api/update/<uuid:poll_id>/', PollUpdateAPIView.as_view(), name='poll-update'),
]

