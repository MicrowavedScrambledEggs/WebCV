from django.test import TestCase
from django.core.exceptions import ValidationError
from . import models
import datetime
from django.utils import timezone
from django.urls.base import reverse

ex_name_1 = "Floor cleaner"
ex_name_2 = "Dish Washing"


def generic_experience(
        name = ex_name_1, type = "Wrk", location = "New World",
        description= "Got some experience with cleaning", 
        start_date = "2010-03-03", end_date = "2011-04-04"):
    return models.Experience.objects.create(
        name=name, type=type, location=location, description=description, 
        start_date = start_date, end_date = end_date)
    
def generic_referee(
        name="Jamie Sam", description="supervisor at new world", 
        email ="jamie.sam@jamiesam.com", phone="+6449999999"):
    return models.Referee.objects.create(
        name=name, description=description, email=email, phone=phone)
    
def generic_skill(
        name="cleaning", stype="hygiene", 
        description="I can clean with good attention to detail"):
    techType = models.SkillType.objects.create(type=stype)
    skill = models.Skill.objects.create(name=name, description=description)
    skill.types =[techType]
    return skill

def set_up_experience_search():
    ex = generic_experience()
    ex2 = generic_experience(name=ex_name_2, location="joe's garage", type="Hob")
    skill = generic_skill()
    models.ExperienceWithSkill.objects.create(
        experience_name=ex, skill_name=skill, 
        description = "scrubbing them floors")
    models.ExperienceWithSkill.objects.create(
        experience_name=ex2, skill_name=skill, 
        description = "cleaning them dishes")

# Create your tests here.
class ExperienceModelTests(TestCase):
    
    def test_end_date_not_before_start_date(self):
        with self.assertRaises(ValidationError):
            generic_experience(end_date="2010-03-03", start_date="2011-04-04")

            
    def test_start_date_not_in_future(self):
        start_date = timezone.now() + datetime.timedelta(days=30)
        end_date = timezone.now() + datetime.timedelta(days=90)
        with self.assertRaises(ValidationError):
            generic_experience(start_date=start_date, end_date=end_date)
        


class ExperienceSearchViewTests(TestCase):
    
    def test_valid_experience_1(self):
        """
        Checks an experience with skills shows up in the experience search context
        when no search has been performed
        """
        ex = generic_experience()
        skill = generic_skill()
        models.ExperienceWithSkill.objects.create(
            experience_name=ex, skill_name=skill, 
            description = "scrubbing them floors")
        response = self.client.get(reverse('badicv:experience search'))
        self.assertQuerysetEqual(
            response.context['exes'], ['<Experience: %s>' % ex_name_1], 
            ordered=False)
        
    def test_valid_experience_2(self):
        """
        Checks experiences with skills shows up in the experience search context
        when no search has been performed
        """
        set_up_experience_search()
        response = self.client.get(reverse('badicv:experience search'))
        self.assertQuerysetEqual(
            response.context['exes'], 
            ['<Experience: %s>' % ex_name_1, '<Experience: %s>' % ex_name_2],
            ordered=False)
        
    def test_invalid_experience_no_skill(self):
        """
        Checks an experience without skills does not show up in the experience 
        search context when no search has been performed
        """
        ex = generic_experience()
        response = self.client.get(reverse('badicv:experience search'))
        self.assertQuerysetEqual(response.context['exes'], [])
        
    
    def test_valid_search_searchterm_name(self):
        """
        Checks view filters experiences by search term and finds name
        """
        set_up_experience_search()
        response = self.client.get(
            reverse('badicv:experience search'), {"search_term": "Floor"})
        self.assertQuerysetEqual(
            response.context['exes'], ['<Experience: %s>' % ex_name_1])    
        
    def test_valid_search_type(self):
        """
        Checks view filters experiences by type
        """
        set_up_experience_search()
        response = self.client.get(
            reverse('badicv:experience search'), {"type": "Hob"})
        self.assertQuerysetEqual(
            response.context['exes'], ['<Experience: %s>' % ex_name_2])    
        
    def test_valid_search_type_searchterm_name(self):
        """
        Checks view filters experiences by type and search term, finding the 
        search term in the name
        """
        set_up_experience_search()
        # create another experience of type hobby that should get filtered
        ex = generic_experience(type="Hob")
        skill = generic_skill()
        models.ExperienceWithSkill.objects.create(
            experience_name=ex, skill_name=skill, 
            description = "scrubbing them floors")
        response = self.client.get(
            reverse('badicv:experience search'), 
            {"type": "Hob", "search_term": "Dish"})
        self.assertQuerysetEqual(
            response.context['exes'], ['<Experience: %s>' % ex_name_2])
        
    def test_valid_search_searchterm_description(self):
        """
        Checks view filters experiences by search term and finds search term in
        description
        """
        set_up_experience_search()
        response = self.client.get(
            reverse('badicv:experience search'), {"search_term": "scrubbing"})
        self.assertQuerysetEqual(
            response.context['exes'], ['<Experience: %s>' % ex_name_1]) 
        
    def test_valid_search_searchterm_location(self):
        """
        Checks view filters experiences by search term and finds search term in
        location
        """
        set_up_experience_search()
        response = self.client.get(
            reverse('badicv:experience search'), {"search_term": "New"})
        self.assertQuerysetEqual(
            response.context['exes'], ['<Experience: %s>' % ex_name_1]) 
        
        