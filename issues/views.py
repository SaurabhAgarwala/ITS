from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from . import forms
from .models import Issue, Comment
from users.models import Team
from .analyze_text import keyPhraseExtraction, namedEntityRecogntion
import json
import time

SIMILARITY_THRESHOLD = 0.5

# Create your views here.

@login_required(login_url="/")
def create_issue(request):
    print('Request Details: ', request)
    print('Request POST: ', request.POST)
    user = request.user
    teams = user.team_set.all()
    if request.method == 'POST':
        if len(teams)==0:
            return get_self_assigned_similar_issues(request)
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

def get_self_assigned_similar_issues(request):
    issues = Issue.objects.filter(team=None, assignee=request.user)
    form = forms.TeamlessIssueForm(request.POST)
    if form.is_valid():
        title = form.cleaned_data['title']
        desc = form.cleaned_data['description']
    print('Starting Text Analysis')
    st_time = time.time()
    keyPhrases, entities = keyPhraseExtraction(title, desc), namedEntityRecogntion(title,desc)
    print('Text Analysis Completed')
    print('Time Taken:', time.time() - st_time)
    text_analysis_params = {}
    text_analysis_params['title_key_phrases'] = keyPhrases['title']
    text_analysis_params['desc_key_phrases'] = keyPhrases['desc']
    text_analysis_params['title_entity_name'] = entities['title']['entityText']
    text_analysis_params['title_entity_type'] = entities['title']['entityType']
    text_analysis_params['desc_entity_name'] = entities['desc']['entityText']
    text_analysis_params['desc_entity_type'] = entities['desc']['entityType']
    similar_issues = []
    # text_analysis_params = {"title_key_phrases": ["one", "two", "three"], "title_entity_name": ["21", "22", "23"], "title_entity_type": ["31", "32", "33"], "desc_key_phrases": ["one", "two", "three"], "desc_entity_name": ["21", "22", "23"], "desc_entity_type": ["31", "32", "33"]}
    for issue in issues:
        if get_issue_similarity_score(issue, text_analysis_params) > SIMILARITY_THRESHOLD:
            similar_issues.append(issue)
    analysed_text_params_json = json.dumps(text_analysis_params)
    print('List of similar issues', similar_issues)
    if len(similar_issues)==0:
        print('1 called')
        request.POST = request.POST.copy()
        request.POST['analysed_text_params'] = analysed_text_params_json
        return create_non_similar_selfassigned_issue(request)
    else:
        print('2 called')
        old_request_params = json.dumps(request.POST)
        print('Old Request Params:', old_request_params)
        context = {
            'similar_issues': similar_issues,
            'analysed_text_params': analysed_text_params_json,
            'team': None,
            'old_request_params': old_request_params
        }
        return render(request, 'issues/similar_issue.html', context)

    
def get_team_similar_issues(request, team):
    issues = Issue.objects.filter(team=team)
    form = forms.PostTeamIssueForm(request.POST)
    if form.is_valid():
        title = form.cleaned_data['title']
        desc = form.cleaned_data['description']
    print('Starting Text Analysis')
    st_time = time.time()
    keyPhrases, entities = keyPhraseExtraction(title, desc), namedEntityRecogntion(title,desc)
    print('Text Analysis Completed')
    print('Time Taken:', time.time() - st_time)
    text_analysis_params = {}
    text_analysis_params['title_key_phrases'] = keyPhrases['title']
    text_analysis_params['desc_key_phrases'] = keyPhrases['desc']
    text_analysis_params['title_entity_name'] = entities['title']['entityText']
    text_analysis_params['title_entity_type'] = entities['title']['entityType']
    text_analysis_params['desc_entity_name'] = entities['desc']['entityText']
    text_analysis_params['desc_entity_type'] = entities['desc']['entityType']
    similar_issues = []
    # text_analysis_params = {"title_key_phrases": ["one", "two", "three"], "title_entity_name": ["21", "22", "23"], "title_entity_type": ["31", "32", "33"], "desc_key_phrases": ["one", "two", "three"], "desc_entity_name": ["21", "22", "23"], "desc_entity_type": ["31", "32", "33"]}
    for issue in issues:
        if get_issue_similarity_score(issue, text_analysis_params) > SIMILARITY_THRESHOLD:
            similar_issues.append(issue)
    analysed_text_params_json = json.dumps(text_analysis_params)
    if len(similar_issues)==0:
        request.POST = request.POST.copy()
        request.POST['analysed_text_params'] = analysed_text_params_json
        return create_non_similar_team_issue(request)
    else:
        print(request.POST)
        assignees = request.POST.getlist('assignee')
        print('Assignees:', assignees)
        data = {}
        for key in request.POST.keys():
            v = request.POST.getlist(key)
            if len(v) == 1:
                v = v[0]
            data[key] = v
        old_request_params = json.dumps(data)
        print('Old Request Params:', old_request_params)
        context = {
            'similar_issues': similar_issues,
            'analysed_text_params': analysed_text_params_json,
            'team': team,
            'old_request_params': old_request_params
        }
        return render(request, 'issues/similar_issue.html', context)


def get_issue_similarity_score(existing_issue, new_issue_params):
    print('Comparing Issue Params:')
    print('Existing Issue Params:', existing_issue)
    print('New Issue Params:', new_issue_params)
    score = 0
    max_score_possible = len(new_issue_params['title_key_phrases']) + len(new_issue_params['title_entity_name']) + len(new_issue_params['desc_key_phrases']) + len(new_issue_params['desc_entity_name'])
    exs_issue_params = json.loads(existing_issue.text_analysis_params)
    for i in range(len(new_issue_params['title_key_phrases'])):
        if new_issue_params['title_key_phrases'][i] in exs_issue_params['title_key_phrases']:
            score += 1
    for i in range(len(new_issue_params['title_entity_name'])):
        if (new_issue_params['title_entity_name'][i] in exs_issue_params['title_entity_name'] and new_issue_params['title_entity_type'][i] in exs_issue_params['title_entity_type']):
            score += 1
    for i in range(len(new_issue_params['desc_key_phrases'])):
        if new_issue_params['desc_key_phrases'][i] in exs_issue_params['desc_key_phrases']:
            score += 1
    for i in range(len(new_issue_params['desc_entity_name'])):
        if (new_issue_params['desc_entity_name'][i] in exs_issue_params['desc_entity_name'] and new_issue_params['desc_entity_type'][i] in exs_issue_params['desc_entity_type']):
            score += 1
    percentage_similarity = score/max_score_possible
    print('Percentage Similarity is:', percentage_similarity, '\n')
    return percentage_similarity


@login_required(login_url="/")
def create_non_similar_selfassigned_issue(request):
    print('self assigned called')
    print('Request Details: ', request)
    print('Request POST: ', request.POST)
    if request.method == 'POST':
        form = forms.TeamlessIssueForm(request.POST)
        if form.is_valid():
            s_instance = form.save()
            s_instance.created_by =  request.user.username
            s_instance.assignee.add(request.user)
            s_instance.text_analysis_params = request.POST['analysed_text_params']
            s_instance.save()
            return redirect('users:userpage')
        else:
            print(form.errors)


@login_required(login_url="/")
def create_selfassigned_issue(request):
    print('self assigned called')
    print('Request Details: ', request)
    print('Request POST: ', request.POST)
    if request.method == 'POST':
        old_params = json.loads(request.POST['old_request_params'])
        print('Old Params', old_params)
        form = forms.TeamlessIssueForm(old_params)
        if form.is_valid():
            s_instance = form.save()
            s_instance.created_by =  request.user.username
            s_instance.assignee.add(request.user)
            s_instance.text_analysis_params = request.POST['analysed_text_params']
            s_instance.save()
            return redirect('users:userpage')
        else:
            print(form.errors)


@login_required(login_url="/")
def create_teamissue(request):
    print('team assigned called')
    print('Request Details: ', request)
    print('Request POST: ', request.POST)
    print('Request data: ', request.body)
    if request.method == 'POST':
        old_params = json.loads(request.POST['old_request_params'])
        print('^^^^^^^^^^^^^^^^^^^^', old_params['assignee'])
        if (len(old_params['assignee'])==1):
            old_params['assignee'] = [old_params['assignee']]
        print('^^^^^^^^^^^^^^^^^^^^', old_params['assignee'])
        print('Old Params', old_params)
        form = forms.PostTeamIssueForm(old_params)
        print('printing', form)
        if form.is_valid():
            print('form is valid')
            s_instance = form.save()
            s_instance.created_by =  request.user.username
            print('creator is', s_instance.created_by, request.user.username)
            team = request.POST.get('team')
            print('team is', team)
            team_obj = Team.objects.get(pk=team)
            s_instance.team = team_obj
            s_instance.text_analysis_params = request.POST['analysed_text_params']
            s_instance.save()
            return redirect('users:userpage')
        else:
            print('error in form')
            print(form.errors)

def create_non_similar_team_issue(request):
    print('@@@@@@@@@@@@@@@@@@yes this is called')
    print('team assigned called')
    print('Request Details: ', request)
    print('Request POST: ', request.POST)
    print('Request data: ', request.body)
    if request.method == 'POST':
        form = forms.PostTeamIssueForm(request.POST)
        if form.is_valid():
            s_instance = form.save()
            s_instance.created_by =  request.user.username
            team = request.POST.get('team')
            team_obj = Team.objects.get(name=team)
            s_instance.team = team_obj
            s_instance.text_analysis_params = request.POST['analysed_text_params']
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
                s_instance.assignee.add(user)
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
