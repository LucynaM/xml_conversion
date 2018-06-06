from django.db import models
from django.contrib.auth.models import User



# Create your models here.
class SprzedazWiersz(models.Model):
    LpSprzedazy = models.IntegerField()
    NrKontrahenta = models.CharField(max_length=30, default='brak')
    NazwaKontrahenta = models.CharField(max_length=240)
    AdresKontrahenta = models.CharField(max_length=240)
    DowodSprzedazy = models.CharField(max_length=240)
    DataWystawienia = models.DateField()
    DataSprzedazy = models.DateField(null=True)
    K_10 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_11 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_12 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_13 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_14 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_15 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_16 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_17 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_18 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_19 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_20 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_21 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_22 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_23 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_24 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_25 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_26 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_27 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_28 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_29 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_30 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_31 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_32 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_33 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_34 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_35 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_36 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_37 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_38 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_39 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    document = models.ForeignKey('LoadedFile', related_name='sales', on_delete=models.CASCADE)

class ZakupWiersz(models.Model):
    LpZakupu = models.IntegerField()
    NrDostawcy = models.CharField(max_length=30, default='brak')
    NazwaDostawcy = models.CharField(max_length=240)
    AdresDostawcy = models.CharField(max_length=240)
    DowodZakupu = models.CharField(max_length=240)
    DataZakupu = models.DateField()
    DataWplywu = models.DateField(null=True)
    K_43 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_44 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_45 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_46 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_47 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_48 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_49 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    K_50 = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    document = models.ForeignKey('LoadedFile', related_name='purchases', on_delete=models.CASCADE)

TYPES = (
    (1, 'VAT'),
    (2, 'KR'),
)

class LoadedFile(models.Model):
    user = models.ForeignKey(User, related_name='file', on_delete=models.CASCADE)
    path = models.FileField(upload_to='files')
    date_creation = models.DateTimeField(auto_now_add=True)
    type = models.IntegerField(choices=TYPES, default=1)

    @property
    def name(self):
        return '{}'.format(self.path.name)
    
class ZOiS(models.Model):
    KodKonta = models.CharField(max_length=256)
    OpisKonta = models.CharField(max_length=256)
    TypKonta = models.CharField(max_length=256)
    KodZespolu = models.CharField(max_length=256)
    OpisZespolu = models.CharField(max_length=256)
    KodKategorii = models.CharField(max_length=256)
    OpisKategorii = models.CharField(max_length=256)
    KodPodkategorii = models.CharField(max_length=256, null=True)
    OpisPodkategorii = models.CharField(max_length=256, null=True)
    BilansOtwarciaWinien = models.DecimalField(max_digits=18, decimal_places=2)
    BilansOtwarciaMa = models.DecimalField(max_digits=18, decimal_places=2)
    ObrotyWinien = models.DecimalField(max_digits=18, decimal_places=2)
    ObrotyMa = models.DecimalField(max_digits=18, decimal_places=2)
    ObrotyWinienNarast = models.DecimalField(max_digits=18, decimal_places=2)
    ObrotyMaNarast = models.DecimalField(max_digits=18, decimal_places=2)
    SaldoWinien = models.DecimalField(max_digits=18, decimal_places=2)
    SaldoMa = models.DecimalField(max_digits=18, decimal_places=2)

class Dziennik(models.Model):
    LpZapisuDziennika = models.IntegerField()
    NrZapisuDziennika = models.CharField(max_length=256, db_index=True)
    OpisDziennika = models.CharField(max_length=256, db_index=True)
    NrDowoduKsiegowego = models.CharField(max_length=256)
    RodzajDowodu = models.CharField(max_length=256)
    DataOperacji = models.DateField()
    DataDowodu = models.DateField()
    DataKsiegowania = models.DateField()
    KodOperatora = models.CharField(max_length=256)
    OpisOperacji = models.CharField(max_length=256)
    DziennikKwotaOperacji = models.DecimalField(max_digits=18, decimal_places=2)


class KontoZapis(models.Model):
    LpZapisu = models.IntegerField()
    NrZapisu = models.ForeignKey(Dziennik, related_name='entries')
    KodKontaWinien = models.CharField(max_length=256, null=True)
    KwotaWinien = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    KwotaWinienWaluta = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    KodWalutyWinien = models.CharField(max_length=256, null=True)
    OpisZapisuWinien = models.CharField(max_length=256, null=True)
    KodKontaMa = models.CharField(max_length=256, null=True)
    KwotaMa = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    KwotaMaWaluta = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    KodWalutyMa = models.CharField(max_length=256, null=True)
    OpisZapisuMa = models.CharField(max_length=256, null=True)