from django.contrib import admin

from .models import Experience, Skill, SkillType, Referee, ExperienceWithSkill, Phone, Email

# Register your models here.
admin.site.register(Experience)
admin.site.register(Skill)
admin.site.register(SkillType)
admin.site.register(Referee)
admin.site.register(ExperienceWithSkill)
admin.site.register(Phone)
admin.site.register(Email)