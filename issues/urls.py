from django.conf.urls import url
from . import views

app_name = 'issues'

urlpatterns = [
   url(r'^newissue/$', views.create_issue, name="new-issue"),
   url(r'^newselfassignedissue/$', views.get_self_assigned_similar_issues, name="new-selfassignedissue"),
   url(r'^newteamissue/(?P<team>[\w-]+)/$$', views.get_team_similar_issues, name="new-teamissue"),
   url(r'^createselfassignedissue/$', views.create_selfassigned_issue, name="create-selfassignedissue"),
   url(r'^createteamissue/$', views.create_teamissue, name="create-teamissue"),
   url(r'^issuedisplay/(?P<id>[\w-]+)/$', views.issue_display, name="issue-disp"),
   url(r'^issueedit/(?P<id>[\w-]+)/$', views.issue_edit, name="issue-edit"),
   url(r'^issuedelete/(?P<id>[\w-]+)/$', views.issue_delete, name="issue-delete"),
   url(r'^comment/(?P<num>[0-9]+)/$', views.comment, name="comment"),
   url(r'^commentreply/(?P<num>[0-9]+)/$', views.commentreply, name="comment-reply"),
]
