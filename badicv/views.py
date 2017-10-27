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
    exes = models.Experience.objects.exclude(experiencewithskill=None)
    if 'type' in request.GET and request.GET['type'] != '':
        exes = exes.filter(type=request.GET['type'])
    if 'search_term' in request.GET and request.GET['search_term'] != "":
        exes = apply_experience_search_term(request.GET['search_term'], exes)
    return render(request, 'badicv/experience_search.html', 
                  context={"exes": exes, "form" : form})

def skill_description(request, skill_name):
    skill = models.Skill.objects.get(name=skill_name)
    return render(request, 'badicv/skill_description.html', 
                  context={"skill": skill})

def skill_search(request):
    form = forms.SkillSearchForm(request.GET)
    skills = models.Skill.objects.exclude(experiencewithskill=None)
    skills = skills.exclude(types=None)
    if 'type' in request.GET and request.GET['type'] != '':
        skills = skills.filter(types__type=request.GET['type'])
    if 'search_term' in request.GET and request.GET['search_term'] != "":
        skills = apply_skill_search_term(request.GET['search_term'], skills)
    return render(request, 'badicv/skill_search.html', 
                  context={"skills": skills, 'form': form})

def referee_list(request):
    refs = models.Referee.objects.exclude(phone=None)
    refs = refs.union(models.Referee.objects.exclude(email=None))
    return render(request, 'badicv/referee_list.html', 
                  context={"refs": refs})

def referee_description(request, referee_name):
    ref = models.Referee.objects.get(name=referee_name)
    return render(request, 'badicv/referee_description.html',
                  context={"ref": ref})

def index(request):
    return render(request, 'badicv/index.html')


# Helper Methods


def apply_experience_search_term(search_term, query_set):
    """
    Method used to search a query set of experiences looking for whole word 
    matches of words in the search term string. Results must have each word in 
    the search term present in at least one of these fields:
        name, location, skills, description, experience with skill description 
    It then orders the results of the search by relevance, comparing results by
    going through the fields in the order above and saying one result is more
    relevant than the other when more words from the search term are in that 
    field
    """
    terms = re.split(r'\s', search_term) # split into list of words
    # flank words in search term by postgres word boundary regex  
    terms = [r'\y%s\y' % term for term in terms]
    for term in terms:
        qName = query_set.filter(name__iregex=term)
        qLoc = query_set.filter(location__iregex=term)
        qSkill = query_set.filter(experiencewithskill__skill__name__iregex=term).distinct()
        qDesc = query_set.filter(description__iregex=term)
        qExSDesc = query_set.filter(experiencewithskill__description__iregex=term).distinct()
        query_set = qName.union(qDesc, qLoc, qSkill, qExSDesc)
        
    def compare_results(r1, r2):
        """
        name > location > skills > description > experience with skill description
        """
        #Whole term match search
        pwholeterm = r'\b%s\b' % search_term #regex for use within python
        wholeterm = r'\y%s\y' % search_term #regex for use within postgres
        r1_count = 0
        r2_count = 0
        scores = {'name':5, 'location':4, 'description': 2}
        for key in scores.keys():
            if r1_count == 0 and re.search(pwholeterm, getattr(r1, key), flags=re.I) != None:
                r1_count = scores[key]
            if r2_count == 0 and re.search(pwholeterm, getattr(r2, key), flags=re.I) != None:
                r2_count = scores[key]
        if r1_count < 3 and r1.experiencewithskill_set.filter(skill__name__iregex=wholeterm).exists():
            r1_count = 3
        if r2_count < 3 and r2.experiencewithskill_set.filter(skill__name__iregex=wholeterm).exists():
            r2_count = 3
        if r1_count == 0 and r1.experiencewithskill_set.filter(description__iregex=wholeterm).exists():
            r1_count = 1
        if r2_count == 0 and r2.experiencewithskill_set.filter(description__iregex=wholeterm).exists():
            r2_count = 1
        if r2_count - r1_count != 0:
            return r2_count - r1_count
        
        # Partial term match search
        # convert to python regex
        pterms = [term.replace(r'\y', r'\b') for term in terms] 
        comp = compare_results_feild(r1, r2, pterms, "name")
        if comp != 0:
            return comp
        comp = compare_results_feild(r1, r2, pterms, "location")
        if comp != 0:
            return comp
        r1_count = 0
        r2_count = 0
        for term in terms:
            if r1.experiencewithskill_set.filter(skill__name__iregex=term).exists():
                r1_count = r1_count + 1
            if r2.experiencewithskill_set.filter(skill__name__iregex=term).exists():
                r2_count = r2_count + 1
        if r2_count - r1_count != 0:
            return r2_count - r1_count
        return compare_results_feild(r1, r2, pterms, "description")
    
    return sorted(query_set, key=cmp_to_key(compare_results))

def compare_results_feild(result1, result2, terms, field):
    r1_count = 0
    r2_count = 0
    for term in terms:
        if re.search(term, getattr(result1, field), flags=re.I) != None:
            r1_count = r1_count + 1
        if re.search(term, getattr(result2, field), flags=re.I) != None:
            r2_count = r2_count + 1
    return r2_count - r1_count

def apply_skill_search_term(search_term, query_set):
    """
    Method used to search a query set of skills looking for whole word 
    matches of words in the search term string. Results must have each word in 
    the search term present in at least one of these fields:
        name, description, skills, experience with skill description 
    It then orders the results of the search by relevance, comparing results by
    going through the fields in the order above and saying one result is more
    relevant than the other when more words from the search term are in that 
    field
    """
    terms = re.split(r'\s', search_term) # split into list of words
    # flank words in search term by postgres word boundary regex  
    terms = [r'\y%s\y' % term for term in terms]
    for term in terms:
        qName = query_set.filter(name__iregex=term)
        qDesc = query_set.filter(description__iregex=term)
        qSkill = query_set.filter(experiencewithskill__experience__name__iregex=term).distinct()
        qExSDesc = query_set.filter(experiencewithskill__description__iregex=term).distinct()
        query_set = qName.union(qDesc, qSkill, qExSDesc)
    
    def compare_results(r1, r2):
        """
        name > description > experience > experience with skill description
        """
        #Whole term match search
        pwholeterm = r'\b%s\b' % search_term #regex for use within python
        wholeterm = r'\y%s\y' % search_term #regex for use within postgres
        r1_count = 0
        r2_count = 0
        scores = {'name':4, 'description': 3}
        for key in scores.keys():
            if r1_count == 0 and re.search(pwholeterm, getattr(r1, key), flags=re.I) != None:
                r1_count = scores[key]
            if r2_count == 0 and re.search(pwholeterm, getattr(r2, key), flags=re.I) != None:
                r2_count = scores[key]
        
        if r1_count < 3:
            exMatch1 = r1.experiencewithskill_set.filter(
                experience__name__iregex=wholeterm).exists()
            if exMatch1:
                r1_count = 2
        if r2_count < 3:
            exMatch2 = r2.experiencewithskill_set.filter(
                experience__name__iregex=wholeterm).exists()
            if exMatch2:
                r2_count = 2
        if r1_count == 0: 
            exMatch1 = r1.experiencewithskill_set.filter(
                description__iregex=wholeterm).exists()
            if exMatch1:
                r1_count = 1
        if r2_count == 0: 
            exMatch2 = r2.experiencewithskill_set.filter(
                description__iregex=wholeterm).exists()
            if exMatch2:
                r2_count = 1
        if r2_count - r1_count != 0:
            return r2_count - r1_count
        
        # Partial term match search
        # convert to python regex
        pterms = [term.replace(r'\y', r'\b') for term in terms] 
        comp = compare_results_feild(r1, r2, pterms, "name")
        if comp != 0:
            return comp
        comp = compare_results_feild(r1, r2, pterms, "description")
        if comp != 0:
            return comp
        r1_count = 0
        r2_count = 0
        for term in terms:
            if r1.experiencewithskill_set.filter(experience__name__iregex=term).exists():
                r1_count = r1_count + 1
            if r2.experiencewithskill_set.filter(experience__name__iregex=term).exists():
                r2_count = r2_count + 1
        return r2_count - r1_count
    
    return sorted(query_set, key=cmp_to_key(compare_results))
    
        