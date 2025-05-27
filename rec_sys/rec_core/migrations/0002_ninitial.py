from django.db import migrations, models
import django.db.models.deletion

def migrate_student_data(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    cursor.execute("""
        UPDATE rec_core_moduleprogress mp
        SET student_id = sp.student_id
        FROM rec_core_studentprogress sp
        WHERE mp.student_progress_id = sp.id
    """)

class Migration(migrations.Migration):

    dependencies = [
        ('rec_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='moduleprogress',
            name='student',
            field=models.ForeignKey(null=True, blank=True, to='rec_core.CustomUser', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.RunPython(migrate_student_data),
        migrations.AlterField(
            model_name='moduleprogress',
            name='student',
            field=models.ForeignKey(to='rec_core.CustomUser', on_delete=django.db.models.deletion.CASCADE),
        ),
    ]
