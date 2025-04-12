from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import CustomUser,Poll
from .serializers import RegisterSerializer, LoginSerializer
from .tokens import get_access_token_for_user
from polls.authentication import CookieJWTAuthentication
from .serializers import PollSerializer,VoteSerializer
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt

CustomUser = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success":True,
                "message": "User registered successfully"
            
                }, status=status.HTTP_201_CREATED)
        return Response({
                "success":False,
                "error": "User failed to register"
            
                }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            access_token = get_access_token_for_user(user)

            response = Response({
                "success": True,
                "message":"user logged in successfully",
                "data": {
                    "access": access_token
                }
                  
            }, status=status.HTTP_200_OK)

            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,  # Set to True in production
                samesite=None,
                max_age=3600
            )

            return response
        
        response = Response({
                "success": False,
                "error":"user failed to logged in",
                  
        }, status=status.HTTP_400_BAD_REQUEST)
        return response
    
    
class CreatePollView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PollSerializer(data=request.data)
        if serializer.is_valid():
            poll = serializer.save(created_by=request.user)
            return Response({
                "success": True,
                "message": "Poll created successfully",
                "data":{
                    "poll_id": str(poll.id)
                }
               
            }, status=status.HTTP_201_CREATED)
        
        response = Response({
                "success": False,
                "error":"failed to create the poll",
                  
        }, status=status.HTTP_400_BAD_REQUEST)  
        return response
    
class VoteCreateView(APIView):
        def post(self, request):
            serializer = VoteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True, 
                    'message': 'Vote recorded'}, status=status.HTTP_201_CREATED)
            return Response({
                'success': False,
                'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        

class MyPollsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        token = request.COOKIES.get('access_token')

        if not token:
            return Response({
                "success":False,
                "error": "Access token not found in cookies."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            email = payload.get('email')

            if not email:
                return Response({
                    "success":False,
                    "error": "Email not found in token."}, status=status.HTTP_400_BAD_REQUEST)

            user = CustomUser.objects.get(email=email)
            polls = Poll.objects.filter(created_by=user).prefetch_related('options')
            serializer = PollSerializer(polls, many=True)
            return Response({
                "success":True,
                "message":"Voted successfully",
                "data":{
                   "values":serializer.data
                }
                }, status=status.HTTP_200_OK)

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, CustomUser.DoesNotExist):
            return Response({
                "success":False,
                "error": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)
        

class PollUpdateAPIView(APIView):
    def put(self, request, poll_id):
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return Response({
                "success":False,
                "error": "Poll not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PollSerializer(poll, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success":True,
                "message":"Updated successfully",
                "data":{
                    "value":serializer.data
                }
            })
        return Response({"success":False,"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
