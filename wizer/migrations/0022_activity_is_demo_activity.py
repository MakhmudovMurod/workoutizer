# Generated by Django 3.0.3 on 2020-05-18 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wizer', '0021_auto_20200430_0645'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='is_demo_activity',
            field=models.BooleanField(default=False, verbose_name='Is this a Demo Activity:'),
        ),
    ]
