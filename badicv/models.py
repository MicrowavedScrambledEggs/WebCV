from django.db import models
from django.core.validators import RegexValidator

# Create your models here.
class SkillType(models.Model):
    type = models.CharField(max_length=32, primary_key=True)
    
    def __str__(self):
        return self.type 
    
    
class Skill(models.Model):
    name = models.CharField(max_length=32, primary_key=True)
    types = models.ManyToManyField(SkillType)
    description = models.TextField()
    
    def __str__(self):
        return self.name
    

class Experience(models.Model):
    type_choice = (("Wrk", "Work"), ("Ed", "Education"), ("Hob", "Hobby"), ("Vol", "Volunteer"))
    name = models.CharField(max_length=64)
    location = models.CharField(max_length=64)
    start_date = models.DateField("Start Date", blank=True)
    end_date = models.DateField("End Date", blank=True)
    description = models.TextField()
    type = models.CharField(max_length=4, choices=type_choice)
    skills = models.ManyToManyField(Skill, through='ExperienceWithSkill')
    
    def __str__(self):
        return self.name
    

class ExperienceWithSkill(models.Model):
    experience_name = models.ForeignKey(Experience, on_delete=models.CASCADE)
    skill_name = models.ForeignKey(Skill, on_delete=models.CASCADE)
    description = models.TextField()
    
    class Meta:
        unique_together = ('experience_name', 'skill_name')
        
    def __str__(self):
        return self.skill_name.name + " experience at " + self.experience_name.name
        

class Referee(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    email = models.EmailField(blank=True)
    phone_regex = RegexValidator(regex=r'^\+?\d{0,2} ?\d? ?\d{3} ?\d{4}$', 
        message="Phone number must be entered in the format: '+999999999' or '+99 9 999 9999'")
    phone_number = models.CharField(validators=[phone_regex], max_length=15, blank=True) # validators should be a list
    experiences = models.ManyToManyField(Experience)
    
    def __str__(self):
        return self.name

    
    

    