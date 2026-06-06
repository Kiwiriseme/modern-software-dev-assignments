import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_default_admin(apps, schema_editor):
    """Create a default admin user and assign all existing records to it."""
    User = apps.get_model("auth", "User")

    admin = User.objects.create_user(
        username="admin@admin.com",
        email="admin@admin.com",
        password="admin123",
    )

    Note = apps.get_model("notes", "Note")
    Todo = apps.get_model("notes", "Todo")
    AISettings = apps.get_model("notes", "AISettings")

    Note.objects.all().update(user=admin)
    Todo.objects.all().update(user=admin)
    AISettings.objects.all().update(user=admin)

    print("\nCreated default admin user: admin@admin.com / admin123")
    print(f"Migrated {Note.objects.count()} notes, {Todo.objects.count()} todos to admin")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("notes", "0003_ai_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="aisettings",
            name="user",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ai_settings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="note",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="todo",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="todos",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(create_default_admin, noop),
        migrations.AlterField(
            model_name="aisettings",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ai_settings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="note",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="todo",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="todos",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
