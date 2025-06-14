# Generated by Django 5.2.1 on 2025-05-23 20:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_path_generator', '0003_learningpath_iscompleted'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LearningPaths',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('deadline', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('category', models.CharField(choices=[('PREREQUISITE', 'Prerequisite'), ('WEEK', 'Weekly Task'), ('RESOURCE', 'Resource')], max_length=20)),
                ('week_number', models.IntegerField(blank=True, null=True)),
                ('day_range', models.CharField(blank=True, max_length=50, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('learning_path', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='learning_path_generator.learningpaths')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
