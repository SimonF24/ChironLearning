from django.conf.urls import url
from django.contrib.contenttypes.views import shortcut

from .views.comments import comment_cancel_vote, comment_done, comment_downvote, comment_upvote, post_comment 
from .views.moderation import (
    flag, flag_done, delete, delete_done, approve, approve_done,
)


urlpatterns = [
    url(r'^post/$', post_comment, name='comments-post-comment'),
    url(r'^posted/$', comment_done, name='comments-comment-done'),
    url(r'^flag/(\d+)/$', flag, name='comments-flag'),
    url(r'^flagged/$', flag_done, name='comments-flag-done'),
    url(r'^delete/(\d+)/$', delete, name='comments-delete'),
    url(r'^deleted/$', delete_done, name='comments-delete-done'),
    url(r'^approve/(\d+)/$', approve, name='comments-approve'),
    url(r'^approved/$', approve_done, name='comments-approve-done'),

    url(r'^cr/(\d+)/(.+)/$', shortcut, name='comments-url-redirect'),

    url(r'^upvote/(\d+)/$', comment_upvote, name='upvote'),
    url(r'^downvote/(\d+)/$', comment_downvote, name='downvote'),
    url(r'^cancel_vote/(\d+)/$', comment_cancel_vote, name='cancel-vote'),
]
