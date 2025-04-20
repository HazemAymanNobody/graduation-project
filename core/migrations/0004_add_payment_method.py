from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20250403_0030'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartorder',
            name='payment_method',
            field=models.CharField(default='cash_on_delivery', max_length=100),
        ),
    ] 