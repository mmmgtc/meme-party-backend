from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('poaster/<str:address>/', views.UserView.as_view()),
    path('memes/', views.MemeList.as_view()),
    path('memes/<int:pk>/', views.MemeView.as_view()),
    path('tags/<str:tag>/', views.TagMemeList.as_view()),
    path('tags/', views.TagList.as_view()),
    path('signup/', views.CustomAuthToken.as_view()),
    path('upvote/', views.UpvoteView.as_view()),
    path('downvote/', views.DownvoteView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
