from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, FriendRequest
from .serializers import UserCreateSerializer, UserSerializer, FriendRequestSerializer, CustomTokenObtainPairSerializer
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

# In-memory store to track friend requests count
import time
friend_requests_timestamps = {}

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserCreateSerializer

class LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    # pagination_class = PageNumberPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()
        if '@' in query:
            return User.objects.filter(email__iexact=query)
        else:
            return User.objects.filter(Q(name__icontains=query))

class FriendRequestView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        target_email = request.data.get('email')
        if not target_email:
            return Response({'error': 'Target email is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target_user = User.objects.get(email=target_email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        current_user = request.user

        # Rate limiting
        current_time = time.time()
        if current_user.id not in friend_requests_timestamps:
            friend_requests_timestamps[current_user.id] = []

        timestamps = friend_requests_timestamps[current_user.id]
        timestamps = [t for t in timestamps if current_time - t < 60]  # Only keep timestamps from the last minute

        if len(timestamps) >= 3:
            return Response({'error': 'Too many friend requests in a minute'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        timestamps.append(current_time)
        friend_requests_timestamps[current_user.id] = timestamps

        # Create FriendRequest
        if FriendRequest.objects.filter(from_user=current_user, to_user=target_user).exists():
            return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

        FriendRequest.objects.create(from_user=current_user, to_user=target_user)
        
        return Response({'success': 'Friend request sent'}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        action = request.data.get('action')
        request_id = request.data.get('request_id')
        try:
            friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        except FriendRequest.DoesNotExist:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'accept':
            friend_request.status = 'accepted'
        elif action == 'reject':
            friend_request.status = 'rejected'
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request.save()
        return Response({'success': 'Friend request updated'}, status=status.HTTP_200_OK)

class FriendListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users who have accepted each other's friend request
        return User.objects.filter(
            Q(sent_requests__status='accepted', sent_requests__to_user=self.request.user) |
            Q(received_requests__status='accepted', received_requests__from_user=self.request.user)
        ).distinct()

class PendingFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Pending friend requests received by the user
        return FriendRequest.objects.filter(to_user=self.request.user, status='pending')
