from django import forms
from .models import Team
from django.contrib.auth.models import User

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        exclude = ['created_by']
    
    def __init__ (self, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)
        self.fields["users"].widget = forms.widgets.CheckboxSelectMultiple()
        # self.fields["users"].help_text = "Members of the team"
        self.fields["users"].queryset = User.objects.all()
        
class TeamEditForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'repository', 'users']

    def __init__ (self, *args, **kwargs):
        super(TeamEditForm, self).__init__(*args, **kwargs)
        self.fields["users"].widget = forms.widgets.CheckboxSelectMultiple()
        # self.fields["users"].help_text = "Members of the team"
        self.fields["users"].queryset = User.objects.all()
        
