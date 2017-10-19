from django.contrib import admin

from .models import Experience, Skill, SkillType, SkillToType, Referees, ExperienceWithSkill

# Register your models here.
admin.site.register(Experience)
admin.site.register(Skill)
admin.site.register(SkillToType)
admin.site.register(SkillType)
admin.site.register(Referees)
admin.site.register(ExperienceWithSkill)