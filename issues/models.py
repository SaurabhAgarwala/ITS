from django.db import models
from django.contrib.auth.models import User
from users.models import Team
from django_mysql.models import ListCharField


# Create your models here.
STATUS = (
    ('Planned', 'Planned'),
    ('In Progress', 'In Progress'),
    ('Done', 'Done'),
)

class Issue(models.Model):
    team = models.ForeignKey(Team,on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    text_analysis_params = models.TextField(blank=True)
    assignee = models.ManyToManyField(User)
    status = models.CharField(max_length=15,choices=STATUS, default='Planned')
    deadline = models.DateField(blank=True, null=True)   
    created_by = models.CharField(max_length=100) 
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=25)
    content = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Comment on %s by %s' % (self.issue.title, self.user.username)

class CommentReply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Reply to %s' % (self.comment)

    class Meta:
        verbose_name_plural = 'Comment Replies'


