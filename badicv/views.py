from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def experience_description(request, experi_name):
    return HttpResponse("Experience page for %s." % experi_name)

def experience_search(request):
    return HttpResponse("Search page for experiences")

def skill_description(request, skill_name):
    return HttpResponse("Skill description page for %s." % skill_name)

def skill_search(request):
    return HttpResponse("Search page for skills")

def referee_list(request):
    return HttpResponse("Referee list")

def index(request):
    return HttpResponse("Home Page")