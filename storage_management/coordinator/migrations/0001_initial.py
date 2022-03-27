# Generated by Django 4.0.3 on 2022-03-26 22:56

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import storage_management.coordinator.utils
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=200, unique=True)),
                ('badge_id', models.CharField(max_length=50)),
                ('banned_until', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Spot',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='coordinator.area')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires_at', models.DateTimeField(default=storage_management.coordinator.utils.seven_days)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='coordinator.member')),
                ('spot', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='coordinator.spot')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('type', models.CharField(choices=[('48_UNTIL_EXPIRED', '48_UNTIL_EXPIRED'), ('24_UNTIL_EXPIRED', '24_UNTIL_EXPIRED'), ('EXPIRED', 'EXPIRED'), ('48_UNTIL_FORFEIT', '48_UNTIL_FORFEIT'), ('24_UNTIL_FORFEIT', '24_UNTIL_FORFEIT'), ('FORFEIT', 'FORFEIT')], max_length=50)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='coordinator.ticket')),
            ],
        ),
        migrations.AddConstraint(
            model_name='ticket',
            constraint=models.UniqueConstraint(condition=models.Q(('finished_at', None)), fields=('member',), name='unique_member'),
        ),
        migrations.AddConstraint(
            model_name='ticket',
            constraint=models.UniqueConstraint(condition=models.Q(('finished_at', None)), fields=('spot',), name='unique_spot'),
        ),
        migrations.AddConstraint(
            model_name='spot',
            constraint=models.UniqueConstraint(fields=('area', 'name'), name='unique_name'),
        ),
    ]