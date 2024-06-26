from django.shortcuts import render
from .serializers import LoginSerializer ,UserSerializer, UserRegistrationSerializer, UserSearchSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from .models import CustomUser, FriendRequest
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta
from django.utils import timezone  


# Create your views here.
class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserSearchView(APIView):
    permission_classes = []
    pagination_class = PageNumberPagination
    serializer_class = UserSearchSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        search_keyword = serializer.validated_data['search_keyword']
        users = CustomUser.objects.filter(email__iexact=search_keyword) | CustomUser.objects.filter(username__icontains=search_keyword)
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)

class SendFrendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get('to_user')

        if not to_user_id:
            return Response({"error": "to_user field is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            to_user = CustomUser.objects.get(id = to_user_id )
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        one_minute_ago = timezone.now() - timedelta(minutes=1)
    
        recent_request = FriendRequest.objects.filter(from_user = request.user, timestamp__gte = one_minute_ago).count()

        if recent_request >= 3:
            return Response({"error": "Too many friend requests. Please wait a while before sending more."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        if FriendRequest.objects.filter(from_user = request.user, to_user = to_user):
             return Response({"error": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)
        import pdb
        pdb.set_trace()
        friend_request = FriendRequest(from_user=request.user, to_user=to_user)
        print(friend_request.id)
        friend_request.save()
        return Response({"success": "Friend request sent."}, status=status.HTTP_201_CREATED)


class AcceptFriendRequest(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        request_id = request.data.get('request_id')
        
        if not request_id:
            return Response({"detail": "request_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
        except FriendRequest.DoesNotExist:
            return Response({"detail": "FriendRequest not found."}, status=status.HTTP_404_NOT_FOUND)
        
       
        if friend_request.from_user != request.user:
            return Response({"detail": "This friend request is not for you."}, status=status.HTTP_403_FORBIDDEN)
      
        friend_request.accepted = True
        friend_request.save()
        return Response({"success": "Friend request accepted."}, status=status.HTTP_200_OK)


class RejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        request_id = request.data.get('request_id')
        
        if not request_id:
            return Response({"detail": "request_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
        except FriendRequest.DoesNotExist:
            return Response({"detail": "FriendRequest not found."}, status=status.HTTP_404_NOT_FOUND)
        
       
        if friend_request.from_user != request.user:
            return Response({"detail": "This friend request is not for you."}, status=status.HTTP_403_FORBIDDEN)
      
        friend_request.delete()
        return Response({"success": "Friend request accepted."}, status=status.HTTP_200_OK)

class ListFriendsView(APIView):
    def get(self,request):
        user =  request.user
        friends_from = FriendRequest.objects.filter(from_user = user, accepted=True).values_list('to_user', flat=True)
        friends_to = FriendRequest.objects.filter(to_user = user, accepted=True).values_list('from_user', flat=True)
        friend_ids = list(friends_from) + list(friends_to)
        friends = CustomUser.objects.filter(id__in=friend_ids)
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

        

class ListPendingFriendRequests(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        pending_requests = FriendRequest.objects.filter(to_user=user, accepted=False)
        pending_request_senders = [request.from_user for request in pending_requests]
        serializer = UserSerializer(pending_request_senders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)