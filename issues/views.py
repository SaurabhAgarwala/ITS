from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from . import forms
from .models import Issue, Comment
from users.models import Team

# Create your views here.

@login_required(login_url="/")
def create_issue(request):
    user = request.user
    teams = user.team_set.all()
    if request.method == 'POST':
        if len(teams)==0:
            form = forms.TeamlessIssueForm(request.POST)
            if form.is_valid():
                s_instance = form.save()
                s_instance.created_by =  request.user.username
                s_instance.assignee = [user]
                s_instance.save()
                return redirect('users:userpage')
        else:
            form = forms.PostTeamForm(request.POST)
            if form.is_valid():
                team = form.cleaned_data['team']
                if team == None:
                    form = forms.TeamlessIssueForm()
                    return render(request, 'issues/selfassigned_issuecreate.html', {'form':form})
                else:
                    team_obj = Team.objects.get(name=team)
                    form = forms.GetTeamIssueForm(team_obj.users)
                    return render(request, 'issues/teamissue_create.html', {'form':form, 'team':team})
    else:
        if len(teams)==0:
            form = forms.TeamlessIssueForm()
            return render(request, 'issues/issue_create.html', {'form':form})
        else:
            form = forms.GetTeamForm(teams)
            return render(request, 'issues/post_teamissue_create.html', {'form':form})

@login_required(login_url="/")
def create_selfassigned_issue(request):
    if request.method == 'POST':
        form = forms.TeamlessIssueForm(request.POST)
        if form.is_valid():
            s_instance = form.save()
            s_instance.created_by =  request.user.username
            s_instance.assignee = [request.user]
            s_instance.save()
            return redirect('users:userpage')

@login_required(login_url="/")
def create_teamissue(request):
    if request.method == 'POST':
        form = forms.PostTeamIssueForm(request.POST)
        if form.is_valid():
            s_instance = form.save()
            s_instance.created_by =  request.user.username
            team = request.POST.get('team')
            team_obj = Team.objects.get(name=team)
            s_instance.team = team_obj
            s_instance.save()
        return redirect('users:userpage')

@login_required(login_url="/")
def issue_display(request,id):
    issue = Issue.objects.get(pk=id)
    comments = issue.comment_set.all()
    assignees = issue.assignee.all()    
    commentform = forms.CommentForm()
    commentreplyform = forms.CommentReplyForm()
    context = {
        'user': request.user,
        'issue': issue,
        'assignees': assignees,
        'comments': comments,
        'commentform': commentform,
        'commentreplyform': commentreplyform
    }
    return render(request, 'issues/issue_display.html', context)

@login_required(login_url="/")
def issue_edit(request, id):  
    issue = Issue.objects.get(pk=id)
    if issue.created_by != request.user.username:
        context = {
            'message': 'You are not allowed to access this page' 
        }
        return render(request, 'message.html', context)
    user = request.user
    teams = user.team_set.all()
    if request.method == 'POST':
        if len(teams)==0:
            form = forms.TeamlessIssueForm(request.POST)
            issue.delete()
            if form.is_valid():
                s_instance = form.save()
                s_instance.created_by =  request.user.username
                s_instance.assignee = [user]
                s_instance.save()
                context = {
                    'message': 'Issue successfully edited.' 
                }
                return render(request, 'message.html', context)
        else:
            form = forms.EditTeamIssueForm(request.POST)
            team = issue.team
            issue.delete()
            if form.is_valid():
                s_instance = form.save()
                s_instance.created_by =  request.user.username
                s_instance.team = team
                s_instance.save()
                context = {
                    'message': 'Team successfully edited.' 
                }
                return render(request, 'message.html', context)
    else:
        if len(teams)==0:
            form = forms.TeamlessIssueForm(instance=issue)
            return render(request, 'issues/issue_edit.html', {'form':form, 'issue':issue})
        else:
            form = forms.EditTeamIssueForm(instance=issue)
            return render(request, 'issues/teamissue_edit.html', {'form':form, 'issue':issue})

@login_required(login_url="/")
def issue_delete(request, id):
    issue = Issue.objects.get(id=id)
    if issue.created_by != request.user.username:
        context = {
            'message': 'You are not allowed to access this page' 
        }
        return render(request, 'message.html', context)
    issue.delete()
    context = {
        'message': 'Issue successfully deleted.' 
    }
    return render(request, 'message.html', context)

@login_required(login_url="/")
def comment(request, num):
    issue = Issue.objects.get(id=num)
    form = forms.CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.issue = issue
        comment.user = request.user
        comment.save()
        return redirect('issues:issue-disp', id=num)

@login_required(login_url="/")
def commentreply(request, num):
    comment = Comment.objects.get(id=num)
    form = forms.CommentReplyForm(request.POST)
    if form.is_valid():
        commentreply = form.save(commit=False)
        commentreply.comment = comment
        commentreply.user = request.user
        commentreply.save()
        return redirect('issues:issue-disp', id=comment.issue.id)
