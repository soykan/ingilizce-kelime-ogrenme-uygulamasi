#!/usr/bin/python3

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.orm.exc import sa_exc
import random
import os
import sys
try:
    from lxml import html
except ImportError:
    print(
        'Programın bazı fonksiyonlarından yararlanabilmek için lxml',
        'kütüphanesini yüklemeniz gerekiyor.'
    )
    if os.name == 'nt':
        print('[python -m pip install lxml]')
    elif os.name == 'posix':
        print('[python3 -m pip install lxml]')
try:
    import requests
except ImportError:
    print(
        'Programın bazı fonksiyonlarından yararlanabilmek için requests',
        'kütüphanesini yüklemeniz gerekiyor.'
    )
    if os.name == 'nt':
        print('[python -m pip install requests]')
    elif os.name == 'posix':
        print('[python3 -m pip install requests]')

last_message = ''
engine = create_engine('sqlite:///kelime-veritabani.db')
Base = declarative_base()


class Kelimeler(Base):
    __tablename__ = 'kelimeler'

    id = Column(Integer, primary_key=True)
    kelime = Column(String, nullable=False)
    anlam = Column(String, nullable=False)
    cumle = Column(String)
    dogru_sayisi = Column(Integer, nullable=False)

    def __repr__(self):
        return 'kelime=%s' % self.kelime


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


class Menu:
    def __init__(self):
        self.secim = 0

    def arayuz_yazdir(self):
        print('''
                                               +-----+-----------------------+
  ▄█     ▄█   ▄█▄  ▄██████▄     ▄██████▄       |  #  |         Menü          |
  ███    ███ ▄███▀ ███    ███   ███    ███     +-----+-----------------------+
  ███▌   ███▐██▀   ███    ███   ███    █▀      | (1) | Kelime ekle           |
  ███▌  ▄█████▀    ███    ███  ▄███            | (2) | Kelime güncelle       |
  ███▌ ▀▀█████▄    ███    ███ ▀▀███ ████▄      | (3) | Kelime sil            |
  ███    ███▐██▄   ███    ███   ███    ███     | (4) | Soru sor              |
  ███    ███ ▀███▄ ███    ███   ███    ███     | (5) | Kelime anlamı sorgula |
  █▀     ███   ▀█▀  ▀██████▀    ████████▀      | (6) | Çıkış                 |
         ▀                                     +-----+-----------------------+
              ''')

    def ekrani_temizle(self):
        if os.name == 'nt':
            os.system('cls')
        elif os.name == 'posix':
            os.system('clear')

    def islem_tercihi(self):
        self.secim = input('Seçiminiz : ')
        while self.secim.isdigit() is False \
                or (int(self.secim) not in range(1, 7)):
            print()
            print('Menüde yapmak istediğiniz işlemin',
                  'solunda kalan sayıyı girin.')
            self.secim = input('Seçiminiz : ')
        return int(self.secim)

    def menu_baslat(self):
        self.ekrani_temizle()
        self.arayuz_yazdir()
        self.secim = self.islem_tercihi()

    def menu_secim(self):
        while (self.secim != 6):
            self.menu_baslat()
            if self.secim == 1:
                KelimeEkle()
            elif self.secim == 2:
                KelimeGuncelle()
            elif self.secim == 3:
                KelimeSil()
            elif self.secim == 4:
                SoruSor()
            elif self.secim == 5:
                KelimeAnlam()
            elif self.secim == 6:
                self.programdan_cikis()
            else:
                self.yanlis_secim()

    def yanlis_secim(self):
        print()
        print('Yanlış seçim!')
        print()

    def programdan_cikis(self):
        sys.exit(0)


class VeritabaniIslemleri():
    def veritabanina_ekle(self, kelime_verisi):
        try:
            session.add(kelime_verisi)
            session.commit()
            return True
        except sa_exc.SQLAlchemyError:
            return False

    def veritabaninda_guncelle(self, kelime, veri):
        try:
            record = session.query(Kelimeler).filter_by(kelime=kelime).first()
            record.kelime = veri.kelime
            record.anlam = veri.anlam
            record.cumle = veri.cumle
            session.commit()
            return True
        except sa_exc.SQLAlchemyError:
            return False

    def veritabanindan_sil(self, kelime):
        try:
            silinecek_kelime = session.query(Kelimeler) \
                .filter_by(kelime=kelime).first()
            session.delete(silinecek_kelime)
            session.commit()
            return True
        except UnmappedInstanceError:
            return False

    def kelime_veritabaninda_mevcut_mu(self, aranan_kelime):
        try:
            for row in session.query(Kelimeler.kelime).all():
                if (row.kelime == aranan_kelime):
                    return True
            return False
        except sa_exc.SQLAlchemyError:
            return False

    def veritabanindan_kayit_getir(self, dogru_sayisi_kosulu):
        kayitlar = session.query(Kelimeler) \
                .filter(Kelimeler.dogru_sayisi < dogru_sayisi_kosulu).all()
        return kayitlar

    def kelimenin_kaydini_getir(self, kelime):
        kayit = session.query(Kelimeler).filter_by(kelime=kelime).first()
        return kayit

    def kaydin_dogru_sayisi_degerini_arttir(self, kelime):
        try:
            record = session.query(Kelimeler) \
                .filter(Kelimeler.kelime == kelime).first()
            record.dogru_sayisi += 1
            session.commit()
            return True
        except sa_exc.SQLAlchemyError:
            return False

    def kaydin_dogru_sayisi_degerini_azalt(self, kelime):
        try:
            record = session.query(Kelimeler) \
                .filter(Kelimeler.kelime == kelime).first()
            record.dogru_sayisi -= 1
            session.commit()
            return True
        except sa_exc.SQLAlchemyError:
            return False


class KelimeEkle():
    def __init__(self):
        self.__kelime = ''
        self.__anlam = ''
        self.__cumle = ''
        self.__veritabani = VeritabaniIslemleri()
        self.kelime_ekle()

    def kelime_ekle(self):
        if self.veri_girisi():
            kelime_verisi = Kelimeler(kelime=self.__kelime,
                                      anlam=self.__anlam,
                                      cumle=self.__cumle,
                                      dogru_sayisi=0)
            self.veritabanina_ekle(kelime_verisi)
        input('Menüye dönmek için ENTER tuşuna basın..')

    def veri_girisi(self):
        self.__kelime = self.kelime_girisi()
        if self.kelime_veritabaninda_mevcut_mu(self.__kelime):
            self.kelime_veritabaninda_mevcut()
            return False
        self.__anlam = self.kelime_anlam_girisi()
        self.__cumle = self.cumle_girisi()
        return True

    def kelime_girisi(self):
        kelime = input('Kelimeyi giriniz : ')
        while kelime.strip() == '':
            kelime = input('İşlem için kelimeyi girmelisiniz : ')
        return kucuk_harfe_cevir(kelime).strip()

    def kelime_veritabaninda_mevcut_mu(self, aranan_kelime):
        return self.__veritabani.kelime_veritabaninda_mevcut_mu(aranan_kelime)

    def kelime_veritabaninda_mevcut(self):
        print('Bu kelime zaten veritabanında mevcut.')
        input('Menüye dönmek için ENTER tuşuna basın..')

    def kelime_anlam_girisi(self):
        anlam = input('Kelimenin anlamını giriniz : ')
        while (anlam.strip() == ''):
            anlam = input('Kelimenin anlamını girmelisiniz : ')
        return kucuk_harfe_cevir(anlam).strip()

    def cumle_girisi(self):
        return input('Kelimenin içinde bulunduğu cümleyi giriniz '
                     '(İsteğe bağlı) : ').strip()

    def veritabanina_ekle(self, kelime_verisi):
        print()
        if self.__veritabani.veritabanina_ekle(kelime_verisi):
            print('Veritabanına eklendi.')
        else:
            print("Hata oluştu, veritabanına eklenemedi.")
        print()


class KelimeGuncelle():
    def __init__(self):
        self.__guncellenecek_kelime = ''
        self.__yeni_kelime = ''
        self.__anlam = ''
        self.__cumle = ''
        self.__veritabani = VeritabaniIslemleri()
        self.kelime_guncelle()

    def kelime_guncelle(self):
        self.__guncellenecek_kelime = self.guncellenecek_kelime_girisi()
        if not self.guncellenecek_kelime_mevcut_mu():
            return
        self.__yeni_kelime = self.yeni_kelime_girisi()
        if self.yeni_kelime_veritabaninda_mevcut_mu():
            return
        self.__anlam = self.yeni_anlam_girisi()
        self.__cumle = self.yeni_cumle_girisi()
        self.veritabaninda_guncelle()

    def guncellenecek_kelime_mevcut_mu(self):
        if self.kelime_veritabaninda_mevcut_mu(self.__guncellenecek_kelime):
            return True
        else:
            self.guncellenecek_kelime_mevcut_degil()
            return False

    def guncellenecek_kelime_mevcut_degil(self):
        print()
        print('Güncellemek istediğiniz kelime veritabanında mevcut değil!')
        print()
        input('Menüye dönmek için ENTER tuşuna basın..')

    def yeni_kelime_zaten_mevcut(self):
        print('Güncellemek üzere yazdığınız yeni kelime',
              'zaten veritabanında mevcut')
        input('Menüye dönmek için ENTER tuşuna basın..')

    def yeni_kelime_veritabaninda_mevcut_mu(self):
        kelimeler_farkli_mi = self.__guncellenecek_kelime != self.__yeni_kelime
        mevcut_mu = self.kelime_veritabaninda_mevcut_mu(self.__yeni_kelime)
        if kelimeler_farkli_mi and mevcut_mu:
            self.yeni_kelime_zaten_mevcut()
            return True
        return False

    def kelime_veritabaninda_mevcut_mu(self, aranan_kelime):
        return self.__veritabani.kelime_veritabaninda_mevcut_mu(aranan_kelime)

    def veritabaninda_guncelle(self):
        kelime = self.__guncellenecek_kelime
        veri = Kelimeler(kelime=self.__yeni_kelime, anlam=self.__anlam,
                         cumle=self.__cumle)
        print()
        if self.__veritabani.veritabaninda_guncelle(kelime, veri):
            print("Veritabanında güncellendi.")
        else:
            print("Hata oluştu. Güncelleme başarısız.")
        print()
        input('Menüye dönmek için ENTER tuşuna basın..')

    def guncellenecek_kelime_girisi(self):
        kelime = input('Güncellenecek kelimeyi giriniz : ')
        while (kelime == ''):
            kelime = input('Güncellenecek kelimeyi girmelisiniz : ')
        kelime = kucuk_harfe_cevir(kelime).strip()
        return kelime

    def yeni_kelime_girisi(self):
        yeni_kelime = input('Yeni kelimeyi giriniz : ')
        while (yeni_kelime.strip() == ''):
            yeni_kelime = input('Yeni kelimeyi girmelisiniz : ')
        return kucuk_harfe_cevir(yeni_kelime).strip()

    def yeni_anlam_girisi(self):
        anlam = input('Yeni kelimenin anlamını giriniz : ')
        while (anlam.strip() == ''):
            anlam = input('Yeni kelimenin anlamını girmelisiniz : ')
        return kucuk_harfe_cevir(anlam).strip()

    def yeni_cumle_girisi(self):
        cumle = input('Yeni kelimenin içinde bulunduğu cümleyi giriniz : ')
        return cumle.strip()


class KelimeSil():
    def __init__(self):
        self.__kelime = ''
        self.__veritabani = VeritabaniIslemleri()
        self.kelime_sil()

    def kelime_sil(self):
        print()
        self.__kelime = self.kelime_girisi()
        self.veritabanindan_sil()
        input('Menüye dönmek için ENTER tuşuna basın..')

    def kelime_girisi(self):
        kelime = input('Silinecek kelimeyi giriniz : ')
        while (kelime.strip() == ''):
            print()
            kelime = input('Silinecek kelimeyi girmelisiniz : ')
        return kucuk_harfe_cevir(kelime).strip()

    def veritabanindan_sil(self):
        if self.__veritabani.veritabanindan_sil(self.__kelime):
            self.veritabanindan_silindi()
        else:
            self.kelime_kayitli_degil()

    def veritabanindan_silindi(self):
        print()
        print("Veritabanından silindi.")
        print()

    def kelime_kayitli_degil(self):
        print()
        print('Silmek istediğiniz kelime kayıtlı değil!')
        print()


class SoruSor():
    def __init__(self):
        self.__kelimeler = []
        self.__anlamlar = []
        self.__cumleler = []
        self.__sorulacak_kelimeler = []
        self.__sorulacak_kelime_sayisi = ''
        self.__dogru_sayisi_kosulu = ''
        self.__cumle_kosulu = ''
        self.__dogru_yanit_sayisi = 0
        self.__yanlis_yanit_sayisi = 0
        self.__veritabani = VeritabaniIslemleri()
        self.soru_sor()

    def soru_sor(self):
        self.dogru_sayisi_kosulu_girisi()
        if not self.sorulacak_kelimenin_verilerini_hazirla():
            return
        if not self.sorulacak_kelime_sayisi_girisi():
            return
        self.cumle_kosulu_belirle()
        self.sorulacak_kelimeleri_belirle()
        self.sorulari_baslat()

    def dogru_sayisi_kosulu_girisi(self):
        soru_mesaji = 'Doğru bilinme sayısı ' \
                      'kaçtan az olan kelimeler sorulsun? : '
        while (self.__dogru_sayisi_kosulu == ''):
            try:
                self.__dogru_sayisi_kosulu = int(input(soru_mesaji))
            except ValueError:
                print('Sadece sayı girmelisiniz.')
                self.__dogru_sayisi_kosulu = ''
                continue

    def sorulacak_kelimenin_verilerini_hazirla(self):
        veritabani = self.__veritabani
        dogru_sayisi_kosulu = self.__dogru_sayisi_kosulu
        kayitlar = veritabani.veritabanindan_kayit_getir(dogru_sayisi_kosulu)
        if self.kosula_uygun_kelime_bulundu_mu(kayitlar):
            return True
        return False

    def kosula_uygun_kelime_bulundu_mu(self, kayitlar):
        if kayitlar == []:
            self.kosula_uygun_kelime_bulunamadi()
            return False
        for kayit in kayitlar:
            self.__kelimeler.append(kayit.kelime)
            self.__anlamlar.append(kayit.anlam)
            self.__cumleler.append(kayit.cumle)
        return True

    def kosula_uygun_kelime_bulunamadi(self):
        print('{0} sayısından daha az doğru sayısına '
              'sahip kelime bulunamadı.'.format(self.__dogru_sayisi_kosulu))
        print()
        input('Menüye dönmek için ENTER tuşuna basın..')

    def sorulacak_kelime_sayisi_girisi(self):
        print()
        while (self.__sorulacak_kelime_sayisi == ''):
            self.__sorulacak_kelime_sayisi = self.kac_kelime_sorulacak()
            if self.__sorulacak_kelime_sayisi == '':
                continue
            if self.sorulacak_kelime_yok():
                return False
        self.yeterince_kelime_mevcut_mu()
        return True

    def kac_kelime_sorulacak(self):
        sorulacak_kelime_sayisi = input('{0} kelimeden kaçı sorulsun? : '
                                        .format(len(self.__kelimeler)))
        try:
            return int(sorulacak_kelime_sayisi)
        except ValueError:
            self.sadece_sayi_girmelisiniz()
            return ''

    def sorulacak_kelime_yok(self):
        if self.__sorulacak_kelime_sayisi <= 0:
            print()
            input('Menüye dönmek için ENTER tuşuna basın..')
            return True
        return False

    def sadece_sayi_girmelisiniz(self):
        print('Sadece sayı girmelisiniz.')

    def yeterince_kelime_mevcut_mu(self):
        if (self.__sorulacak_kelime_sayisi > len(self.__kelimeler)):
            self.__sorulacak_kelime_sayisi = len(self.__kelimeler)
            self.eldeki_kadar_kelime_sorulacak()

    def eldeki_kadar_kelime_sorulacak(self):
        sorulacak_kelime_sayisi = self.__sorulacak_kelime_sayisi
        print('{0} kelime sorulacak!'.format(sorulacak_kelime_sayisi))

    def cumle_kosulu_belirle(self):
        cumle_kosulu = input('Kelimelerin yanında cümle verilsin mi? (E/H) : ')
        self.__cumle_kosulu = cumle_kosulu.strip()
        print()

    def sorulacak_kelimeleri_belirle(self):
        for i in range(0, self.__sorulacak_kelime_sayisi):
            self.sorulacak_kelime_ekle()

    def sorulacak_kelime_ekle(self):
        kelimeler = self.__kelimeler
        sorulacak_kelime = kelimeler[random.randrange(0, len(kelimeler))]
        while (sorulacak_kelime in self.__sorulacak_kelimeler):
            sorulacak_kelime = kelimeler[random.randrange(0, len(kelimeler))]
        self.__sorulacak_kelimeler.append(sorulacak_kelime)

    def sorulari_baslat(self):
        for kelime in self.__sorulacak_kelimeler:
            self.cumle_isteniyorsa_yazdir(kelime)
            anlam = self.kelimenin_anlamini_sor(kelime)
            self.yaniti_degerlendir(kelime, anlam)
        self.sonucu_yazdir()
        input('Menüye dönmek için ENTER tuşuna basın..')

    def cumle_isteniyorsa_yazdir(self, kelime):
        cumle_kosulu = self.__cumle_kosulu
        cumleler = self.__cumleler
        kelimeler = self.__kelimeler
        if (cumle_kosulu == 'E' or cumle_kosulu == 'e'):
            print(cumleler[kelimeler.index(kelime)])

    def kelimenin_anlamini_sor(self, kelime):
        anlam = input(kelime + ' : ')
        return anlam.strip()

    def yaniti_degerlendir(self, kelime, yanit):
        anlam = self.kelimenin_anlamini_getir(kelime)
        anlam = kucuk_harfe_cevir(anlam)
        yanit = kucuk_harfe_cevir(yanit)
        if self.yanitin_dogru_olma_kosulu(yanit, anlam):
            self.dogru_yanit_islemleri(kelime)
        else:
            self.yanlis_yanit_islemleri(kelime)

    def kelimenin_anlamini_getir(self, kelime):
        return self.__anlamlar[self.__kelimeler.index(kelime)]

    def yanitin_dogru_olma_kosulu(self, yanit, anlam):
        anlam_degeri_girilmis_mi = yanit.strip() != ''
        anlam_dogru_mu = yanit in anlam
        kosul = anlam_degeri_girilmis_mi and anlam_dogru_mu
        return kosul

    def dogru_yanit_islemleri(self, kelime):
        self.yanit_dogru(kelime)
        self.dogru_yanit_sayisini_arttir(kelime)

    def yanlis_yanit_islemleri(self, kelime):
        self.yanit_yanlis(kelime)
        self.dogru_yanit_sayisini_azalt(kelime)

    def yanit_dogru(self, kelime):
        anlamlar = self.__anlamlar
        kelimeler = self.__kelimeler
        print()
        print('Yanıt doğru!')
        print('[' + anlamlar[kelimeler.index(kelime)] + ']')
        print()

    def dogru_yanit_sayisini_arttir(self, kelime):
        veritabani = self.__veritabani
        if not veritabani.kaydin_dogru_sayisi_degerini_arttir(kelime):
            print('Hata oluştu : Kelimenin doğru bilinme sayısı '
                  'veritabanında arttırılamadı.')
        self.__dogru_yanit_sayisi += 1

    def yanit_yanlis(self, kelime):
        anlamlar = self.__anlamlar
        kelimeler = self.__kelimeler
        dogru_yanit = anlamlar[kelimeler.index(kelime)]
        print()
        print('Yanıt yanlış!')
        print('Doğru yanıt {0} olacaktı.'.format(dogru_yanit))
        print()

    def dogru_yanit_sayisini_azalt(self, kelime):
        veritabani = self.__veritabani
        if not veritabani.kaydin_dogru_sayisi_degerini_azalt(kelime):
            print('Hata oluştu : Kelimenin doğru bilinme sayısı '
                  'veritabanında azaltılamadı.')
        self.__yanlis_yanit_sayisi += 1

    def sonucu_yazdir(self):
        sorulacak_kelime_sayisi = self.__sorulacak_kelime_sayisi
        dogru_yanit_sayisi = self.__dogru_yanit_sayisi
        yanlis_yanit_sayisi = self.__yanlis_yanit_sayisi
        print('{0} sorudan {1} tanesine doğru {2} tanesine yanlış '
              'yanıt verdiniz!'.format(sorulacak_kelime_sayisi,
                                       dogru_yanit_sayisi,
                                       yanlis_yanit_sayisi))


class KelimeAnlam():
    def __init__(self):
        self.__veritabani = VeritabaniIslemleri()
        self.__page = None
        self.__tree = None
        self.__kelime_mevcudiyet = False
        self.__kelime = ''
        self.__kategoriler = []
        self.__kelimeler = []
        self.__anlamlar = []
        self.__anlam = []
        self.__euaksu = 0  # euaksu = en_uzun_anlamin_karakter_sayisi_uzunlugu
        self.kelime_anlam()

    def kelime_anlam(self):
        self.__kelime = self.kelime_girisi()
        self.kelime_veritabaninda_mevcutsa_yazdir(self.__kelime)
        self.__page = self.sayfayi_getir()
        if self.__page is None:
            return
        self.__tree = self.parse_edilmis_html_verisini_getir()
        if self.__tree is None:
            return
        if not self.kelimeye_ait_bulunan_verileri_al():
            return
        self.anlam_degerlerini_hazirla()
        self.bulunan_anlamlari_yazdir()
        if self.kelime_mevcut_mu():
            return
        if not self.veritabanina_eklensin_mi():
            return

    def kelime_girisi(self):
        print()
        aranan = input('Anlamını öğrenmek istediğiniz kelimeyi giriniz : ')
        while (aranan.strip() == ''):
            aranan = input('Anlamını öğrenmek istediğiniz '
                           'kelimeyi girmelisiniz : ')
            print()
        return kucuk_harfe_cevir(aranan).strip()

    def kelime_veritabaninda_mevcutsa_yazdir(self, kelime):
        veritabani = self.__veritabani
        kayit = veritabani.kelimenin_kaydini_getir(kelime)
        if kayit is not None:
            self.__kelime_mevcudiyet = True
            self.veritabanindaki_kaydi_yazdir(kayit)
        print()

    def veritabanindaki_kaydi_yazdir(self, kayit):
        print()
        print('# Veritabanındaki Kayıtlar #')
        print()
        print('Kelime : {0}'.format(kayit.kelime))
        print('Anlam : {0}'.format(kayit.anlam))
        print('Cümle : {0}'.format(kayit.cumle))

    def sayfayi_getir(self):
        try:
            page = requests.get('http://tureng.com/en/turkish-english/{0}'
                                .format(self.__kelime,))
            return page
        except NameError:
            self.requests_kutuphanesi_eksik()
            return None

    def requests_kutuphanesi_eksik(self):
        print()
        print('requests kütüphanesini yüklemelisiniz!')
        print('[python -m pip install requests]')
        print()
        input('Menüye dönmek için ENTER tuşuna basın..')

    def parse_edilmis_html_verisini_getir(self):
        try:
            tree = html.fromstring(self.__page.content)
            return tree
        except NameError:
            self.lxml_kutuphanesi_eksik()
            return None

    def lxml_kutuphanesi_eksik(self):
        print()
        print('lxml kütüphanesini yüklemelisiniz!')
        print('[python -m pip install lxml]')
        print()
        input('Menüye dönmek için ENTER tuşuna basın..')

    def kelimeye_ait_bulunan_verileri_al(self):
        kelimeler, anlamlar = self.verileri_ayikla()
        if (len(anlamlar) == 0 or ((self.__kelime in anlamlar) and
                                   self.__kelime not in kelimeler)):
            self.kelimenin_anlami_bulunamadi()
            return False
        return True

    def verileri_ayikla(self):
        tree = self.__tree
        self.__kategoriler = tree.xpath('//td[@class="hidden-xs"]/text()')
        self.__kelimeler = tree.xpath('//td[@class="en tm"]/a/text()')
        self.__anlamlar = tree.xpath('//td[@class="tr ts"]/a/text()')
        return self.__kelimeler, self.__anlamlar

    def kelimenin_anlami_bulunamadi(self):
        print("Tureng'de belirttiğiniz kelimenin anlamı bulunamadı!")
        print()
        input('Menüye dönmek için ENTER tuşuna basın..')

    def anlam_degerlerini_hazirla(self):
        aranan = self.__kelime
        kelimeler = self.__kelimeler
        anlamlar = self.__anlamlar
        anlam = self.__anlam
        for i in range(0, len(kelimeler)):
            if (kelimeler[i] == aranan and anlamlar[i] not in anlam):
                anlam.append(anlamlar[i])
                self.euaksu_belirle(anlamlar[i])

    # en uzun anlam değerinin uzunluğunu tespit eder
    def euaksu_belirle(self, anlam):
        if len(anlam) > self.__euaksu:
            self.__euaksu = len(anlam)

    def bulunan_anlamlari_yazdir(self):
        self.tablo_basligini_yazdir()
        self.tablo_satirlarini_yazdir()

    def tablo_basligini_yazdir(self):
        euaksu = self.__euaksu
        print()
        print('# Tureng Dictionary #')
        print()
        print('    Category' + 12 * ' ' + 'English' + 13 * ' ' + 'Turkish')
        print('------------' + 12 * '-' + '-------' + 13 * '-' + euaksu * '-')

    def tablo_satirlarini_yazdir(self):
        for i in range(0, len(self.__anlam)):
            self.tablo_satirini_yazdir(i)

    def tablo_satirini_yazdir(self, index):
        i = index
        kategoriler = self.__kategoriler
        kelimeler = self.__kelimeler
        anlam = self.__anlam
        print(str(i + 1) + (4 - len(str(i+1))) * ' ', end='')
        print(kategoriler[i] + (20 - len(kategoriler[i])) * ' ', end='')
        print(kelimeler[i] + (20 - len(kelimeler[i])) * ' ', end='')
        print(anlam[i])
        if (i == 9 or i == 19 or i == 29 or i == 39 or i == 49 or i == 59):
            daha_fazla = input("Devamı için [ENTER]'a basın")

    def kelime_mevcut_mu(self):
        if self.__kelime_mevcudiyet:
            self.menuye_don()
        return self.__kelime_mevcudiyet

    def menuye_don(self):
        print()
        input('Menüye dönmek için ENTER tuşuna basın..')

    def veritabanina_eklensin_mi(self):
        print()
        eklensin_mi = input('Bulduğunuz kelime ve anlamları '
                            'veritabanına eklensin mi (E/H) ? : ')
        print()
        if (eklensin_mi == 'E' or eklensin_mi == 'e'):
            self.veritabanina_ekle()
            return True
        self.menuye_don()
        return False

    def veritabanina_ekle(self):
        sira_numaralari = self.sira_numaralarini_hazirla()
        while (self.sira_numaralari_kontrol(sira_numaralari) is False):
            sira_numaralari = self.sira_numaralarini_hazirla()
        self.secilenleri_veritabanina_kaydet(sira_numaralari)

    def eklenecek_anlamlar_girisi(self):
        eklenecek_anlamlar = ''
        while (eklenecek_anlamlar == ''):
            eklenecek_anlamlar = input('Eklemek istediğiniz kelimenin '
                                       'anlamlarının sıra numaralarını '
                                       'virgülle ayırarak giriniz : ')
        return eklenecek_anlamlar

    def sira_numaralarini_hazirla(self):
        eklenecek_anlamlar = self.eklenecek_anlamlar_girisi()
        eklenecek_anlamlar = self.bosluklari_sil(eklenecek_anlamlar)
        return self.virgule_gore_ayirarak_listele(eklenecek_anlamlar)

    def bosluklari_sil(self, eklenecek_anlamlar):
        return ''.join(eklenecek_anlamlar.split())

    def virgule_gore_ayirarak_listele(self, eklenecek_anlamlar):
        return eklenecek_anlamlar.split(',')

    def sira_numaralari_kontrol(self, sira_numaralari):
        for i in sira_numaralari:
            if not i.isdigit():
                print('Yanlış değer girdiniz!')
                print()
                return False
            elif int(i) <= 0 or int(i) > len(self.__anlam):
                print('Yanlış sıra numarası girdiniz!')
                print()
                return False
        return True

    def secilenleri_veritabanina_kaydet(self, sira_numaralari):
        kelime_verisi = self.kelime_verisini_hazirla(sira_numaralari)
        if self.__veritabani.veritabanina_ekle(kelime_verisi):
            self.veritabanina_eklendi()
        else:
            self.veritabanina_eklenirken_hata()

    def kelime_verisini_hazirla(self, sira_numaralari):
        eklenecek_anlamlar = self.eklenecek_anlamlari_hazirla(sira_numaralari)
        self.eklenecek_anlamlari_yazdir(eklenecek_anlamlar)
        cumle = self.cumle_girisi()
        kelime_verisi = Kelimeler(kelime=self.__kelime,
                                  anlam=eklenecek_anlamlar,
                                  cumle=cumle,
                                  dogru_sayisi=0)
        return kelime_verisi

    def eklenecek_anlamlari_hazirla(self, sira_numaralari):
        eklenecek_anlamlar = []
        anlam = self.__anlam
        for i in sira_numaralari:
            eklenecek_anlamlar.append(anlam[int(i) - 1])
        eklenecek_anlamlar = ', '.join(eklenecek_anlamlar)
        return eklenecek_anlamlar

    def eklenecek_anlamlari_yazdir(self, eklenecek_anlamlar):
        print()
        print('Eklenecek anlamlar :', eklenecek_anlamlar)
        print()

    def cumle_girisi(self):
        cumle = input('Kelimenin içinde geçtiği bir cümle giriniz '
                      '(İsteğe bağlı) : ')
        print()
        return cumle

    def veritabanina_eklendi(self):
        print()
        print('Veritabanına eklendi.')
        print()
        self.menuye_don()

    def veritabanina_eklenirken_hata(self):
        print()
        print('Hata : Veritabanına eklenemedi.')
        print()
        self.menuye_don()


def kucuk_harfe_cevir(metin):
    lower_map = {
        ord('I'): 'ı',
        ord('İ'): 'i'
        }
    metin = metin.translate(lower_map).lower()
    return metin

if __name__ == '__main__':
    Menu().menu_secim()
