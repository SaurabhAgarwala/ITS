from django.conf.urls import url
from . import views

app_name = 'users'

urlpatterns = [
   url(r'^signup/$', views.signup_view, name="signup"),
   url(r'^login/$', views.login_view, name="login"),
   url(r'^logout/$', views.logout_view, name="logout"),
   url(r'^newteam/$', views.create_team, name="new-team"),
   url(r'^userpage/$', views.userpage, name="userpage"),
   url(r'^teamdisplay/(?P<id>[\w-]+)/$', views.team_display, name="team-disp"),
   url(r'^teamedit/(?P<id>[\w-]+)/$', views.team_edit, name="team-edit"),
   url(r'^teamdelete/(?P<id>[\w-]+)/$', views.team_delete, name="team-delete"),
]