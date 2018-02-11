'''
Created on 23/10/2017

@author: Admin
'''
from django import forms
from . import models

class ExperienceSearchForm(forms.Form):
    
    search_term = forms.CharField(label='search', required=False)
    choices = [('','')]
    choices.extend(models.Experience.type_choice)
    type = forms.ChoiceField(choices=tuple(choices), required=False)
    

class SkillSearchForm(forms.Form):
    
    search_term = forms.CharField(label='search', required=False)
    choices = [('','')]
    choices.extend([(sk.skill_type, sk.skill_type) for sk in models.SkillType.objects.all()])
    type = forms.ChoiceField(choices=tuple(choices), required=False)
