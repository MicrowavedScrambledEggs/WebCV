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
    return HttpResponse("Skill description page for %s." % skill_name)

def skill_search(request):
    return HttpResponse("Search page for skills")

def referee_list(request):
    return HttpResponse("Referee list")

def index(request):
    return render(request, 'badicv/index.html')