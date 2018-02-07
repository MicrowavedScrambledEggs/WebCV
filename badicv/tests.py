from django.test import TestCase
from django.core.exceptions import ValidationError
from . import models
import datetime
from django.utils import timezone
from django.urls.base import reverse

ex_name_1 = "Floor cleaner"
ex_name_2 = "Dish Washing"


def generic_experience(
        name = ex_name_1, extype = "Wrk", location = "New World",
        description= "Responsible for keeping the supermarket tidy", 
        start_date = "2010-03-03", end_date = "2011-04-04"):
    return models.Experience.objects.create(
        name=name, ex_type=extype, location=location, description=description, 
        start_date = start_date, end_date = end_date)
    
def generic_referee(
        name="Jamie Sam", description="supervisor at new world", 
        email ="jamie.sam@jamiesam.com", phone="+6449999999"):
    ref = models.Referee.objects.create(name=name, description=description)
    models.Email.objects.create(email=email, referee=ref)
    models.Phone.objects.create(phone_number=phone, referee=ref)
    return ref
    
def generic_skill(
        name="cleaning", stype="hygiene", 
        description="I can clean with good attention to detail"):
    skillType, result = models.SkillType.objects.get_or_create(skill_type=stype)
    skill = models.Skill.objects.create(name=name, description=description)
    skill.types =[skillType]
    return skill

def generic_experience_and_skill(
        name = ex_name_1, extype = "Wrk", location = "New World",
        description= "Responsible for keeping the supermarket tidy", 
        start_date = "2010-03-03", end_date = "2011-04-04",
        sname="cleaning", stype="hygiene", 
        sdescription="I can clean with good attention to detail", 
        exsdescription="scrubbing them floors"
        ):
    ex = models.Experience.objects.create(
        name=name, ex_type=extype, location=location, description=description, 
        start_date = start_date, end_date = end_date)
    if models.Skill.objects.filter(name=sname).exists():
        skill = models.Skill.objects.get(name=sname)
    else:
        skill = generic_skill(name=sname, stype=stype, description=sdescription)
    models.ExperienceWithSkill.objects.create(
        experience=ex, skill=skill, description=exsdescription)
    return ex, skill

def set_up_experience_search():
    ex = generic_experience()
    ex2 = generic_experience(name=ex_name_2, location="joe's garage", extype="Hob")
    skill = generic_skill()
    models.ExperienceWithSkill.objects.create(
        experience=ex, skill=skill, 
        description = "scrubbing them floors")
    models.ExperienceWithSkill.objects.create(
        experience=ex2, skill=skill, 
        description = "cleaning them dishes")
    return ex, ex2, skill

def enumerate_search_term_experience():
    terms = ["blue", "bled", 'blood', "bugs", "black"]
    values = [["she", "sells", "sea", "shells", "shore"] for i in range(5)]
    experiences = []
    
    def recursive_helper(i, j):
        values[j][i] = terms[i]
        if i == len(terms) - 1:
            name = "%s %d" % (' '.join(values[0]), len(experiences) +1)
            experiences.append(generic_experience_and_skill(
                name = name, location=' '.join(values[1]), 
                sname=' '.join(values[2]), description=' '.join(values[3]), 
                exsdescription=' '.join(values[4]))[0])
        else:
            recursive_helper(i + 1, j)
        values[j][i] = "shell"
        if j < len(values) - 1:
            recursive_helper(i, j + 1)
    
    recursive_helper(0, 0)
    return experiences

def enumerate_search_term_skill():
    terms = ["bled", 'blood', "bugs", "black"]
    values = [["she", "sells", "sea", "shells"] for i in range(4)]
    skills = []
    
    def recursive_helper(i, j):
        values[j][i] = terms[i]
        if i == len(terms) - 1:
            name = "%s %d" % (' '.join(values[0]), len(skills) +1)
            skills.append(generic_experience_and_skill(
                sname = name, name=' '.join(values[2]), 
                sdescription=' '.join(values[1]), 
                exsdescription=' '.join(values[3]))[1])
        else:
            recursive_helper(i + 1, j)
        values[j][i] = "shell"
        if j < len(values) - 1:
            recursive_helper(i, j + 1)
    
    recursive_helper(0, 0)
    return skills
            

# Create your tests here.
class ExperienceModelTests(TestCase):
    
    def test_end_date_not_before_start_date(self):
        with self.assertRaises(ValidationError):
            generic_experience(end_date="2010-03-03", start_date="2011-04-04").clean()

            
    def test_start_date_not_in_future(self):
        start_date = timezone.now() + datetime.timedelta(days=30)
        end_date = timezone.now() + datetime.timedelta(days=90)
        with self.assertRaises(ValidationError):
            generic_experience(start_date=start_date, end_date=end_date).clean()
        


class ExperienceSearchViewTests(TestCase):
    
    def test_valid_experience_1(self):
        """
        Checks an experience with skills shows up in the experience search context
        when no search has been performed
        """
        ex = generic_experience()
        skill = generic_skill()
        models.ExperienceWithSkill.objects.create(
            experience=ex, skill=skill, 
            description = "scrubbing them floors")
        response = self.client.get(reverse('badicv:experience search'))
        self.assertQuerysetEqual(
            response.context['exes'], ['<Experience: %s>' % ex_name_1], 
            ordered=False)
        
    def test_valid_experience_2(self):
        """
        Checks all experiences with skills shows up in the experience search 
        context when no search has been performed
        Note: may change behaviour in future to just show key experiences
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
        ex1, ex2, skill = set_up_experience_search()
        # create another experience of type hobby that should get filtered
        ex3 = generic_experience(extype="Hob")
        models.ExperienceWithSkill.objects.create(
            experience=ex3, skill=skill, 
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
        
    def test_valid_search_searchterm_skill(self):
        """
        Checks view filters experiences by search term and finds search term in
        list of skills
        """
        ex1, ex2, skill = set_up_experience_search()
        skill2 = generic_skill(name="customer service")
        models.ExperienceWithSkill.objects.create(
            experience=ex1, skill=skill2, 
            description = "Helping clients with cleaning products")
        response = self.client.get(
            reverse('badicv:experience search'), {"search_term": "customer"})
        self.assertQuerysetEqual(
            response.context['exes'], ['<Experience: %s>' % ex_name_1])
        
    def test_valid_search_searchterm_exwithskilldescription(self):
        """
        Checks view filters experiences by search term and finds search term in
        the description of experience with skill
        """
        ex1, ex2, skill = set_up_experience_search()
        skill2 = generic_skill(name="customer service")
        models.ExperienceWithSkill.objects.create(
            experience=ex1, skill=skill2, 
            description = "Helping clients with cleaning products")
        response = self.client.get(
            reverse('badicv:experience search'), {"search_term": "clients"})
        self.assertQuerysetEqual(
            response.context['exes'], ['<Experience: %s>' % ex_name_1])
        
    def test_search_ordering_whole_phrase(self):
        """
        Tests that the ordering of search results by which field has a complete  
        match of the search term is correct 
        name > location > skills > description > experience with skill description 
        """
        search_term = "Black Bugs Blood"
        item_no = 1
        keywords = ["location", "sname", "description", "exsdescription"]
        expected_ordering = [generic_experience_and_skill(name=search_term)[0]]
        for keyword in keywords:
            expected_ordering.append(generic_experience_and_skill(
                **{"name": "Test ex %d" % item_no, keyword: search_term})[0])
            item_no = item_no + 1
        response = self.client.get(
            reverse('badicv:experience search'), {"search_term": search_term})
        self.assertListEqual(response.context['exes'], expected_ordering)
        
    def test_search_ordering_whole_phrase_before_part_match(self):
        """
        Tests that the ordering of search results by which field has a complete  
        match of the search term and which field has partial matches of the search
        term is correct 
        name > location > skills > description > experience with skill description 
        """
        item_no = 1
        search_term = "Black bugs blood bled blue"
        keywords = ["location", "sname", "description", "exsdescription"]
        expected_ordering = [generic_experience_and_skill(name=search_term)[0]]
        for keyword in keywords:
            expected_ordering.append(generic_experience_and_skill(
                **{"name": "Test ex %d" % item_no, keyword: search_term})[0])
            item_no = item_no + 1    
        expected_ordering.extend(enumerate_search_term_experience())
        response = self.client.get(
            reverse('badicv:experience search'), {"search_term": search_term})
        self.assertListEqual(response.context['exes'], expected_ordering)
        
    def test_search_ordering_part_match(self):
        """
        Tests that the ordering of search results by which fields have partial  
        matches of the search term is correct 
        name > location > skills > description > experience with skill description 
        """
        experiences = enumerate_search_term_experience()
        search_term = "Black bugs blood bled blue"
        response = self.client.get(
            reverse('badicv:experience search'), {"search_term": search_term})
        self.assertListEqual(response.context['exes'], experiences)
        

class SkillSearchViewTests(TestCase):
    
    maxDiff = None
    
    def test_invalid_skills_no_experience(self):
        """
        Test that skills without associated experiences do not show up in the 
        view
        """
        ex, skill = generic_experience_and_skill()
        generic_skill(name="skill two")
        response = self.client.get(reverse('badicv:skill search'))
        self.assertQuerysetEqual(response.context['skills'], ['<Skill: %s>' % skill.name])
        
    def test_invalid_skills_no_type(self):
        """
        Test that skills without at least one type do not show up in the view
        """
        ex, skill = generic_experience_and_skill()
        models.Skill.objects.create(name="name", description="description")
        response = self.client.get(reverse('badicv:skill search'))
        self.assertQuerysetEqual(response.context['skills'], ['<Skill: %s>' % skill.name])
        
    def test_search_searchterm_no_part_word(self):
        """
        test that only whole word matches turn up in the search and not
        part word matches
        """
        ex, skill = generic_experience_and_skill()
        response = self.client.get(
            reverse('badicv:skill search'), {"search_term": "clea"})
        self.assertQuerysetEqual(response.context['skills'], [])
        
    def test_no_search(self):
        """
        Test that full list of skills shows when no search made.
        NOTE: may change no search behaviour in future to show just key skills
        """
        ex, skill = generic_experience_and_skill()
        response = self.client.get(reverse('badicv:skill search'))
        self.assertQuerysetEqual(response.context['skills'], ['<Skill: %s>' % skill.name])
        
    def test_search_type(self):
        """
        Test that search results get filtered by type selected
        """
        ex, skill = generic_experience_and_skill()
        ex2, skill2 = generic_experience_and_skill(
            name=ex_name_2, sname="skill two", stype="technical")
        response = self.client.get(
            reverse('badicv:skill search'), {"type": "hygiene"})
        self.assertQuerysetEqual(response.context['skills'], ['<Skill: %s>' % skill.name])
        
    def test_search_searchterm_name(self):
        """
        Tests that search term is found in skill name and results are filtered
        accordingly
        """
        ex, skill = generic_experience_and_skill()
        ex2, skill2 = generic_experience_and_skill(
            name=ex_name_2, sname="skill two", stype="technical")
        response = self.client.get(
            reverse('badicv:skill search'), {"search_term": "two"})
        self.assertQuerysetEqual(response.context['skills'], ['<Skill: %s>' % skill2.name])

    def test_search_type_searchterm_name(self):
        """
        Tests that search term is found in skill name and results are filtered
        by both search term and type
        """
        ex, skill = generic_experience_and_skill()
        ex2, skill2 = generic_experience_and_skill(
            name=ex_name_2, sname="skill two", stype="technical")
        ex3, skill3 = generic_experience_and_skill(
            name=ex_name_2, sname="skill three", stype="hygiene")
        response = self.client.get(
            reverse('badicv:skill search'), 
            {"search_term": "skill", "type": "technical"})
        self.assertQuerysetEqual(response.context['skills'], ['<Skill: %s>' % skill2.name])
        
    def test_search_searchterm_description(self):
        """
        Tests that search term is found in skill description and results are 
        filtered accordingly
        """
        ex, skill = generic_experience_and_skill()
        ex2, skill2 = generic_experience_and_skill(
            name=ex_name_2, sname="skill two", sdescription= "description")
        response = self.client.get(
            reverse('badicv:skill search'), {"search_term": "good"})
        self.assertQuerysetEqual(response.context['skills'], ['<Skill: %s>' % skill.name])
        
    def test_search_searchterm_experience(self):
        """
        Tests that search term is found in names of associated experiences and 
        results are filtered accordingly
        """
        ex, skill = generic_experience_and_skill()
        ex2, skill2 = generic_experience_and_skill(
            name=ex_name_2, sname="skill two")
        response = self.client.get(
            reverse('badicv:skill search'), {"search_term": "Dish"})
        self.assertQuerysetEqual(response.context['skills'], ['<Skill: %s>' % skill2.name])
        
    def test_search_searchterm_experiencewithskill_descripition(self):
        """
        Tests that search term is found in descriptions of experience with skill
        and results are filtered accordingly
        """
        ex, skill = generic_experience_and_skill()
        ex2, skill2 = generic_experience_and_skill(
            name=ex_name_2, sname="skill two", exsdescription= "banana")
        response = self.client.get(
            reverse('badicv:skill search'), {"search_term": "banana"})
        self.assertQuerysetEqual(response.context['skills'], ['<Skill: %s>' % skill2.name])
        
    def test_searchterm_ordering_whole_term(self):
        """
        Test search results where the whole search term matches a skill's field
        is ordered appropriately by which field matched
        name > description > experience > experience with skill description
        """
        item_no = 1
        search_term = "Black bugs blood bled"
        keywords = ["sdescription", "name", "exsdescription"]
        expected_ordering = [generic_experience_and_skill(sname=search_term)[1]]
        for keyword in keywords:
            expected_ordering.append(generic_experience_and_skill(
                **{"sname": "Test skill %d" % item_no, keyword: search_term})[1])
            item_no = item_no + 1 
        response = self.client.get(
            reverse('badicv:skill search'), {"search_term": search_term})
        self.assertListEqual(response.context['skills'], expected_ordering)
        
    def test_searchterm_ordering_part_term(self):
        """
        Test search results where parts of a search term matches a skill's field
        (and for each word in the search term there is a field of the skill with 
        the word) is ordered appropriately by which field matched the most words
        name > description > experience > experience with skill description
        """
        skills = enumerate_search_term_skill()
        search_term = "Black bugs blood bled"
        response = self.client.get(
            reverse('badicv:skill search'), {"search_term": search_term})
        self.assertListEqual(response.context['skills'], skills)
        
    def test_searchterm_ordering_whole_part_term(self):
        """
        Test search results where there are both skills where the whole search
        term can be found in one field and skills where the search term is 
        matched across fields is ordered appropriately, with whole matches before
        part matches 
        """
        item_no = 1
        search_term = "Black bugs blood bled"
        keywords = ["sdescription", "name", "exsdescription"]
        expected_ordering = [generic_experience_and_skill(sname=search_term)[1]]
        for keyword in keywords:
            expected_ordering.append(generic_experience_and_skill(
                **{"sname": "Test skill %d" % item_no, keyword: search_term})[1])
            item_no = item_no + 1
        expected_ordering.extend(enumerate_search_term_skill()) 
        response = self.client.get(
            reverse('badicv:skill search'), {"search_term": search_term})
        self.assertListEqual(response.context['skills'], expected_ordering)
        

class ReferenceViewTests(TestCase):
    
    def test_valid_ref_displayed(self):
        ref = generic_referee()
        ref2 = generic_referee(name="Joe Swanson")
        response = self.client.get(reverse('badicv:referee list'))
        self.assertQuerysetEqual(
            response.context['refs'], 
            ['<Referee: %s>' % ref.name, '<Referee: %s>' % ref2.name],
            ordered=False)
    
    def test_invalid_ref(self):
        models.Referee.objects.create(name="no", description="dice")
        response = self.client.get(reverse('badicv:referee list'))
        self.assertQuerysetEqual(response.context['refs'], [])
        
    def test_valid_ref_2(self):
        ref = models.Referee.objects.create(name="no", description="dice")
        models.Phone.objects.create(phone_number="+6449999999", referee=ref)
        response = self.client.get(reverse('badicv:referee list'))
        self.assertQuerysetEqual(
            response.context['refs'], ['<Referee: %s>' % ref.name])
        
    def test_valid_ref_3(self):
        ref = models.Referee.objects.create(name="no", description="dice")
        models.Email.objects.create(email="jamie.sam@jamiesam.com", referee=ref)
        response = self.client.get(reverse('badicv:referee list'))
        self.assertQuerysetEqual(
            response.context['refs'], ['<Referee: %s>' % ref.name])
    
        
        
        
        
    
        
     
        
        