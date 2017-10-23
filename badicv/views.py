from django.shortcuts import render
from django.http import HttpResponse

from . import models, forms
from functools import cmp_to_key
import re

# Create your views here.
def experience_description(request, experi_name):
    ex = models.Experience.objects.get(name=experi_name)
    return render(request, 'badicv/experience_description.html', 
                  context={"ex": ex})

def experience_search(request):
    form = forms.ExperienceSearchForm(request.GET)
    exes = models.Experience.objects.all() # if nothing searched, show all
    if 'search_term' in request.GET and request.GET['search_term'] != "":
        exes = apply_search_term(request.GET['search_term'], exes)
    if 'type' in request.GET and request.GET['type'] != '':
        exes = exes.filter(type=request.GET['type'])
    return render(request, 'badicv/experience_search.html', 
                  context={"exes": exes, "form" : form})

def skill_description(request, skill_name):
    skill = models.Skill.objects.get(name=skill_name)
    return render(request, 'badicv/skill_description.html', 
                  context={"skill": skill})

def skill_search(request):
    form = forms.SkillSearchForm(request.GET)
    skills = models.Skill.objects.all() #if nothing searched, show all
    if 'search_term' in request.GET and request.GET['search_term'] != "":
        skills = apply_search_term(request.GET['search_term'], skills)
    if 'type' in request.GET and request.GET['type'] != '':
        skills = skills.filter(types__type=request.GET['type'])
    return render(request, 'badicv/skill_search.html', 
                  context={"skills": skills, 'form': form})

def referee_list(request):
    return render(request, 'badicv/referee_list.html', 
                  context={"refs": models.Referee.objects.all()})

def referee_description(request, referee_name):
    ref = models.Referee.objects.get(name=referee_name)
    return render(request, 'badicv/referee_description.html',
                  context={"ref": ref})

def index(request):
    return render(request, 'badicv/index.html')

def apply_search_term(search_term, query_set):
    """
    Method used to search a query set of a model with a name and description field
    looking for whole word matches of words in the search term string. It then 
    orders the results of the search by how many of the words in search term are
    in the name
    """
    terms = re.split(r'\s', search_term) # split into list of words
    # flank words in search term by postgres word boundary regex  
    terms = [r'\y%s\y' % term for term in terms]
    for term in terms:
        qName = query_set.filter(name__iregex=term)
        qDesc = query_set.filter(description__iregex=term)
        query_set = qName.union(qDesc)
        
    def compare_results(r1, r2):
        r1_count = 0
        r2_count = 0
        for term in terms:
            term = term.replace(r'\y', r'\b') # convert to python regex
            if re.search(term, r1.name, flags=re.I) != None:
                r1_count = r1_count + 1
            if re.search(term, r2.name, flags=re.I) != None:
                r2_count = r2_count + 1
        return r2_count - r1_count
    
    return sorted(query_set, key=cmp_to_key(compare_results))
        