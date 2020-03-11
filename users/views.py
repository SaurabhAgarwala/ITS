from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from . import forms
from .models import Team

# Create your views here.
def signup_view(request):
    if request.method == 'POST' :
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:userpage')
    else:
        form = UserCreationForm()
    context = {'form':form}
    return render(request, 'users/signup_page.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('users:userpage')
    else:
        form = AuthenticationForm()
    context = {'form':form}    
    return render(request, 'homepage.html', context)

def logout_view(request):
        logout(request)
        return redirect('login')

@login_required(login_url="/")
def create_team(request):
    if request.method == 'POST':
        form = forms.TeamForm(request.POST)
        # print(type(members))
        # print(len(members))
        # print(members)
        if form.is_valid():
            s_instance = form.save()
            s_instance.created_by =  request.user.username
            # s_instance.users = members
            s_instance.save()
        # return render(request, 'users/post_url.html', {'e_url':e_url})
        return redirect('issues:new-issue')
    else:
        form = forms.TeamForm
    context = {'form':form}
    return render(request, 'users/team_create.html', context)

@login_required(login_url="/")
def userpage(request):
    user = request.user
    teams = user.team_set.all()
    issues = user.issue_set.all()
    
    context = {
        'user': user,
        'teams': teams,
        'issues': issues
    }
    return render(request, 'users/userpage.html', context)

@login_required(login_url="/")
def team_display(request,id):  
    team = Team.objects.get(pk=id)
    users = team.users.all()
    issues = team.issue_set.all()
    context = {
        'user': request.user,
        'team': team,
        'users': users,
        'issues': issues
    }
    return render(request, 'users/team_display.html', context)

@login_required(login_url="/")
def team_edit(request, id):  
    team = Team.objects.get(pk=id)
    if team.created_by != request.user.username:
        context = {
            'message': 'You are not allowed to access this page' 
        }
        return render(request, 'message.html', context)
    if request.method == 'POST':
        form = forms.TeamEditForm(request.POST)
        team.delete()
        if form.is_valid():
            s_instance = form.save()
            s_instance.created_by =  request.user.username
            # s_instance.users = members
            s_instance.save()
        # return render(request, 'users/post_url.html', {'e_url':e_url})
        context = {
            'message': 'Team successfully edited.' 
        }
        return render(request, 'message.html', context)
    else:
        form = forms.TeamEditForm(instance=team)
        context = {'form':form, 'team': team}
        return render(request, 'users/team_edit.html', context)

@login_required(login_url="/")
def team_delete(request, id):
    team = Team.objects.get(id=id)
    if team.created_by != request.user.username:
        context = {
            'message': 'You are not allowed to access this page' 
        }
        return render(request, 'message.html', context)
    team.delete()
    context = {
        'message': 'Team successfully deleted.' 
    }
    return render(request, 'message.html', context)