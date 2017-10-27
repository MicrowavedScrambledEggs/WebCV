from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

# Create your models here.
class SkillType(models.Model):
    skill_type = models.CharField(max_length=32, primary_key=True)
    
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
    ex_type = models.CharField(max_length=4, choices=type_choice)
    skills = models.ManyToManyField(Skill, through='ExperienceWithSkill')
    
    def clean(self):
        if type(self.start_date) is str:
            self.start_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        if type(self.end_date) is str:
            self.end_date = datetime.strptime(self.end_date, "%Y-%m-%d").date()
        if self.start_date > timezone.now().date():
            raise ValidationError("Start date can not be in future")
        if self.start_date > self.end_date:
            raise ValidationError("Start date can not be after end date")        
    
    def __str__(self):
        return self.name
    

class ExperienceWithSkill(models.Model):
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    description = models.TextField()
    
    class Meta:
        unique_together = ('experience', 'skill')
        
    def __str__(self):
        return self.skill.name + " experience at " + self.experience.name
        

class Referee(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    experiences = models.ManyToManyField(Experience)
    
    def __str__(self):
        return self.name
    

class Phone(models.Model):
    referee = models.ForeignKey(Referee, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?\d{0,2} ?\d? ?\d{3} ?\d{4}$', 
        message="Phone number must be entered in the format: '+999999999' or '+99 9 999 9999'")
    phone_number = models.CharField(validators=[phone_regex], max_length=15, blank=True)


class Email(models.Model):
    referee = models.ForeignKey(Referee, on_delete=models.CASCADE)
    email = models.EmailField()
    

    