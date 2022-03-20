# Generated by Django 4.0.2 on 2022-03-04 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinator', '0006_alter_member_email_alter_notification_created_at_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='ticket',
            constraint=models.UniqueConstraint(condition=models.Q(('finished_at', None)), fields=('spot',), name='unique_spot'),
        ),
    ]
