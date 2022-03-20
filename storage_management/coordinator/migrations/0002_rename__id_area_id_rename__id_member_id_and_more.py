# Generated by Django 4.0.2 on 2022-02-20 06:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coordinator', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='area',
            old_name='_id',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='member',
            old_name='_id',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='notification',
            old_name='_id',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='spot',
            old_name='_id',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='ticket',
            old_name='_id',
            new_name='id',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='ticket_id',
        ),
        migrations.RemoveField(
            model_name='spot',
            name='area_id',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='member_id',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='spot_id',
        ),
        migrations.AddField(
            model_name='notification',
            name='ticket',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='notifications', to='coordinator.ticket'),
        ),
        migrations.AddField(
            model_name='spot',
            name='area',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='spots', to='coordinator.area'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='member',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='tickets', to='coordinator.member'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='spot',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='tickets', to='coordinator.spot'),
        ),
    ]
