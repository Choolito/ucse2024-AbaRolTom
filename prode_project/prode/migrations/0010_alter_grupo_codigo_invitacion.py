# Generated by Django 5.1 on 2024-09-13 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prode', '0009_alter_grupo_codigo_invitacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grupo',
            name='codigo_invitacion',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
