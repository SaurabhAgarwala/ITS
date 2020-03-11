from django.contrib import admin
from .models import Issue, Comment, CommentReply

# Register your models here.
admin.site.register(Issue)
admin.site.register(Comment)
admin.site.register(CommentReply)
