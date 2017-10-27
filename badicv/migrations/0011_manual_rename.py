from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('badicv', '0010_auto_20171026_1634'),
    ]

    operations = [
        migrations.RenameField(
            model_name='experience',
            old_name='type',
            new_name='ex_type',
        ),
		migrations.RenameField(
            model_name='skilltype',
            old_name='type',
            new_name='skill_type',
        ),
    ]