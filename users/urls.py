
from django.urls import path
from .views import SignUpView, LoginView, UserSearchView, SendFrendRequestView, AcceptFriendRequest, RejectFriendRequestView, ListFriendsView, ListPendingFriendRequests
urlpatterns = [
   path('signup/', SignUpView.as_view(), name='signup'),
   path('login/', LoginView.as_view(), name='login'),
   path('search/', UserSearchView.as_view(), name='user-search'),
   path('send_friend_request/', SendFrendRequestView.as_view(), name='send_friend_request'),
   path('Accept_friend_request/', AcceptFriendRequest.as_view(), name='Accept_friend_request'),
   path('Reject_friend_request/', RejectFriendRequestView.as_view(), name='Reject_friend_request'),
   path('List_friend/', ListFriendsView.as_view(), name='List_friend'),
   path('List_pending_friend_request/', ListPendingFriendRequests.as_view(), name='List_pending_friend_request')
]
