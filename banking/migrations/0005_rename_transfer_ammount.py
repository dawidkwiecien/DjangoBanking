from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("banking", "0004_transfer_states"),
    ]

    operations = [
        migrations.RenameField(
            model_name="transfer",
            old_name="ammount",
            new_name="amount",
        ),
    ]
