from django.db import models


class Photo(models.Model):
    image = models.ImageField(upload_to='photos/', verbose_name='Снимка')
    filename = models.CharField(max_length=255, verbose_name='Име на файл')
    datetime_taken = models.DateTimeField(null=True, blank=True, verbose_name='Дата и час на заснемане')

    # Използваме DecimalField за координати (най-подходящо за GPS)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                   verbose_name='Географска ширина')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                    verbose_name='Географска дължина')

    has_gps = models.BooleanField(default=False, verbose_name='Има GPS данни')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата на качване')

    def __str__(self):
        return self.filename