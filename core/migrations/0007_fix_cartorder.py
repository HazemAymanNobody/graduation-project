from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20250403_0112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartorder',
            name='payment_method',
            field=models.CharField(default='cash_on_delivery', max_length=100),
        ),
    ] 