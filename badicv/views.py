from django.shortcuts import render
from django.http import HttpResponse

from . import models

# Create your views here.
def experience_description(request, experi_name):
    ex = models.Experience.objects.get(name=experi_name)
    return render(request, 'badicv/experience_description.html', 
                  context={"ex": ex})

def experience_search(request):
    return render(request, 'badicv/experience_search.html', 
                  context={"exes": models.Experience.objects.all()})

def skill_description(request, skill_name):
    skill = models.Skill.objects.get(name=skill_name)
    return render(request, 'badicv/skill_description.html', 
                  context={"skill": skill})

def skill_search(request):
    return render(request, 'badicv/skill_search.html', 
                  context={"skills": models.Skill.objects.all()})

def referee_list(request):
    return render(request, 'badicv/referee_list.html', 
                  context={"refs": models.Referee.objects.all()})

def referee_description(request, referee_name):
    ref = models.Referee.objects.get(name=referee_name)
    return render(request, 'badicv/referee_description.html',
                  context={"ref": ref})

def index(request):
    return render(request, 'badicv/index.html')