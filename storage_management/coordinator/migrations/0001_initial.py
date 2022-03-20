# Generated by Django 4.0.2 on 2022-02-20 03:50

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=200)),
                ('badge_id', models.CharField(max_length=50)),
                ('banned_until', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Spot',
            fields=[
                ('_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('area_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='coordinator.area')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('finished_at', models.DateTimeField()),
                ('member_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='coordinator.member')),
                ('spot_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='coordinator.spot')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=100)),
                ('ticket_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='coordinator.ticket')),
            ],
        ),
    ]
