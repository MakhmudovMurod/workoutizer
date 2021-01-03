# Generated by Django 3.0.8 on 2020-12-29 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("wizer", "0007_auto_20201229_1033"),
    ]

    operations = [
        migrations.CreateModel(
            name="BestSectionType",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("description", models.CharField(max_length=600)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="BestSection",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_index", models.IntegerField()),
                ("end_index", models.IntegerField()),
                ("max_value", models.FloatField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("activity", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="wizer.Activity")),
                (
                    "secion_type",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="wizer.BestSectionType"),
                ),
            ],
        ),
    ]
