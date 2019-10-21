#!/usr/bin/python3

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.orm.exc import sa_exc
from lxml import html
import requests
import random
import os
import sys


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
    __session = None

    @classmethod
    def veritabanini_hazirla(cls):
        engine = create_engine('sqlite:///kelime-veritabani.db')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        cls.__session = Session()

    @classmethod
    def veritabanina_ekle(cls, kelime_verisi):
        try:
            cls.__session.add(kelime_verisi)
            cls.__session.commit()
            return True
        except sa_exc.SQLAlchemyError:
            return False

    @classmethod
    def veritabaninda_guncelle(cls, kelime, veri):
        try:
            session = cls.__session
            record = session.query(Kelimeler).filter_by(kelime=kelime).first()
            record.kelime = veri.kelime
            record.anlam = veri.anlam
            record.cumle = veri.cumle
            session.commit()
            return True
        except sa_exc.SQLAlchemyError:
            return False

    @classmethod
    def veritabanindan_sil(cls, kelime):
        try:
            silinecek_kelime = cls.__session.query(Kelimeler) \
                .filter_by(kelime=kelime).first()
            cls.__session.delete(silinecek_kelime)
            cls.__session.commit()
            return True
        except UnmappedInstanceError:
            return False

    @classmethod
    def kelime_veritabaninda_mevcut_mu(cls, aranan_kelime):
        try:
            for row in cls.__session.query(Kelimeler.kelime).all():
                if (row.kelime == aranan_kelime):
                    return True
            return False
        except sa_exc.SQLAlchemyError:
            return False

    @classmethod
    def veritabanindan_kayit_getir(cls, dogru_sayisi_kosulu):
        kayitlar = cls.__session.query(Kelimeler) \
                .filter(Kelimeler.dogru_sayisi < dogru_sayisi_kosulu).all()
        return kayitlar

    @classmethod
    def kelimenin_kaydini_getir(cls, kelime):
        session = cls.__session
        kayit = session.query(Kelimeler).filter_by(kelime=kelime).first()
        return kayit

    @classmethod
    def kaydin_dogru_sayisi_degerini_arttir(cls, kelime):
        try:
            record = cls.__session.query(Kelimeler) \
                .filter(Kelimeler.kelime == kelime).first()
            record.dogru_sayisi += 1
            cls.__session.commit()
            return True
        except sa_exc.SQLAlchemyError:
            return False

    @classmethod
    def kaydin_dogru_sayisi_degerini_azalt(cls, kelime):
        try:
            record = cls.__session.query(Kelimeler) \
                .filter(Kelimeler.kelime == kelime).first()
            record.dogru_sayisi -= 1
            cls.__session.commit()
            return True
        except sa_exc.SQLAlchemyError:
            return False


class IO():
    @staticmethod
    def menuye_don():
        input('Menüye dönmek için ENTER tuşuna basın..')

    @staticmethod
    def requests_kutuphanesi_eksik():
        print()
        print('requests kütüphanesini yüklemelisiniz!')
        print('[python3 -m pip install requests]')
        print()
        IO.menuye_don()

    @staticmethod
    def lxml_kutuphanesi_eksik():
        print()
        print('lxml kütüphanesini yüklemelisiniz!')
        print('[python3 -m pip install lxml]')
        print()
        IO.menuye_don()


class KelimeEkleIO():
    @staticmethod
    def kelime_girisi():
        kelime = input('Kelimeyi giriniz : ')
        while kelime.strip() == '':
            kelime = input('İşlem için kelimeyi girmelisiniz : ')
        return kucuk_harfe_cevir(kelime).strip()

    @staticmethod
    def kelime_veritabaninda_mevcut():
        print('Bu kelime zaten veritabanında mevcut.')

    @staticmethod
    def kelime_anlam_girisi():
        anlam = input('Kelimenin anlamını giriniz : ')
        while (anlam.strip() == ''):
            anlam = input('Kelimenin anlamını girmelisiniz : ')
        return kucuk_harfe_cevir(anlam).strip()

    @staticmethod
    def cumle_girisi():
        return input('Kelimenin içinde bulunduğu cümleyi giriniz '
                     '(İsteğe bağlı) : ').strip()

    @staticmethod
    def veritabanina_eklendi():
        print()
        print('Veritabanına eklendi.')
        print()

    @staticmethod
    def veritabanina_eklenemedi():
        print()
        print("Hata oluştu, veritabanına eklenemedi.")
        print()


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
        IO.menuye_don()

    def veri_girisi(self):
        self.__kelime = KelimeEkleIO.kelime_girisi()
        if self.kelime_veritabaninda_mevcut_mu(self.__kelime):
            KelimeEkleIO.kelime_veritabaninda_mevcut()
            return False
        self.__anlam = KelimeEkleIO.kelime_anlam_girisi()
        self.__cumle = KelimeEkleIO.cumle_girisi()
        return True

    def kelime_veritabaninda_mevcut_mu(self, aranan_kelime):
        return self.__veritabani.kelime_veritabaninda_mevcut_mu(aranan_kelime)

    def veritabanina_ekle(self, kelime_verisi):
        if self.__veritabani.veritabanina_ekle(kelime_verisi):
            KelimeEkleIO.veritabanina_eklendi()
        else:
            KelimeEkleIO.veritabanina_eklenemedi()


class KelimeGuncelleIO():
    @staticmethod
    def guncellenecek_kelime_girisi():
        kelime = input('Güncellenecek kelimeyi giriniz : ')
        while (kelime == ''):
            kelime = input('Güncellenecek kelimeyi girmelisiniz : ')
        kelime = kucuk_harfe_cevir(kelime).strip()
        return kelime

    @staticmethod
    def guncellenecek_kelime_mevcut_degil():
        print()
        print('Güncellemek istediğiniz kelime veritabanında mevcut değil!')
        print()
        input('Menüye dönmek için ENTER tuşuna basın..')

    @staticmethod
    def yeni_kelime_girisi():
        yeni_kelime = input('Yeni kelimeyi giriniz : ')
        while (yeni_kelime.strip() == ''):
            yeni_kelime = input('Yeni kelimeyi girmelisiniz : ')
        return kucuk_harfe_cevir(yeni_kelime).strip()

    @staticmethod
    def yeni_kelime_zaten_mevcut():
        print('Güncellemek üzere yazdığınız yeni kelime',
              'zaten veritabanında mevcut')
        input('Menüye dönmek için ENTER tuşuna basın..')

    @staticmethod
    def yeni_anlam_girisi():
        anlam = input('Yeni kelimenin anlamını giriniz : ')
        while (anlam.strip() == ''):
            anlam = input('Yeni kelimenin anlamını girmelisiniz : ')
        return kucuk_harfe_cevir(anlam).strip()

    @staticmethod
    def yeni_cumle_girisi():
        cumle = input('Yeni kelimenin içinde bulunduğu cümleyi giriniz : ')
        return cumle.strip()

    @staticmethod
    def veritabaninda_guncellendi():
        print()
        print("Veritabanında güncellendi.")
        print()

    @staticmethod
    def guncelleme_basarisiz():
        print()
        print("Hata oluştu. Güncelleme başarısız.")
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
        guncellenecek_kelime = KelimeGuncelleIO.guncellenecek_kelime_girisi()
        self.__guncellenecek_kelime = guncellenecek_kelime
        if not self.guncellenecek_kelime_mevcut_mu():
            return
        self.__yeni_kelime = KelimeGuncelleIO.yeni_kelime_girisi()
        if self.yeni_kelime_veritabaninda_mevcut_mu():
            return
        self.__anlam = KelimeGuncelleIO.yeni_anlam_girisi()
        self.__cumle = KelimeGuncelleIO.yeni_cumle_girisi()
        self.veritabaninda_guncelle()

    def guncellenecek_kelime_mevcut_mu(self):
        if self.kelime_veritabaninda_mevcut_mu(self.__guncellenecek_kelime):
            return True
        else:
            KelimeGuncelleIO.guncellenecek_kelime_mevcut_degil()
            return False

    def yeni_kelime_veritabaninda_mevcut_mu(self):
        kelimeler_farkli_mi = self.__guncellenecek_kelime != self.__yeni_kelime
        mevcut_mu = self.kelime_veritabaninda_mevcut_mu(self.__yeni_kelime)
        if kelimeler_farkli_mi and mevcut_mu:
            KelimeGuncelleIO.yeni_kelime_zaten_mevcut()
            return True
        return False

    def kelime_veritabaninda_mevcut_mu(self, aranan_kelime):
        return self.__veritabani.kelime_veritabaninda_mevcut_mu(aranan_kelime)

    def veritabaninda_guncelle(self):
        kelime = self.__guncellenecek_kelime
        veri = Kelimeler(kelime=self.__yeni_kelime, anlam=self.__anlam,
                         cumle=self.__cumle)
        if self.__veritabani.veritabaninda_guncelle(kelime, veri):
            KelimeGuncelleIO.veritabaninda_guncellendi()
        else:
            KelimeGuncelleIO.guncelleme_basarisiz()
        IO.menuye_don()


class KelimeSilIO():
    @staticmethod
    def veritabanindan_silindi():
        print()
        print("Veritabanından silindi.")
        print()

    @staticmethod
    def kelime_kayitli_degil():
        print()
        print('Silmek istediğiniz kelime kayıtlı değil!')
        print()

    @staticmethod
    def kelime_girisi():
        kelime = input('Silinecek kelimeyi giriniz : ')
        while (kelime.strip() == ''):
            print()
            kelime = input('Silinecek kelimeyi girmelisiniz : ')
        return kucuk_harfe_cevir(kelime).strip()


class KelimeSil():
    def __init__(self):
        self.__kelime = ''
        self.__veritabani = VeritabaniIslemleri()
        self.kelime_sil()

    def kelime_sil(self):
        print()
        self.__kelime = KelimeSilIO.kelime_girisi()
        self.veritabanindan_sil()
        IO.menuye_don()

    def veritabanindan_sil(self):
        if self.__veritabani.veritabanindan_sil(self.__kelime):
            KelimeSilIO.veritabanindan_silindi()
        else:
            KelimeSilIO.kelime_kayitli_degil()


class SoruSorIO():
    @staticmethod
    def dogru_sayisi_kosulu_girisi():
        soru_mesaji = 'Doğru bilinme sayısı ' \
                      'kaçtan az olan kelimeler sorulsun? : '
        while (True):
            try:
                return int(input(soru_mesaji))
            except ValueError:
                print('Sadece sayı girmelisiniz.')

    @staticmethod
    def kosula_uygun_kelime_bulunamadi(dogru_sayisi_kosulu):
        print('{0} sayısından daha az doğru sayısına '
              'sahip kelime bulunamadı.'.format(dogru_sayisi_kosulu))
        print()
        IO.menuye_don()

    @staticmethod
    def kelime_sayisi_girisi(kelime_sayisi):
        sorulacak_kelime_sayisi = input('{0} kelimeden kaçı sorulsun? : '
                                        .format(kelime_sayisi))
        return sorulacak_kelime_sayisi

    @staticmethod
    def sorulacak_kelime_yok():
        print()
        IO.menuye_don()

    @staticmethod
    def sadece_sayi_girmelisiniz():
        print('Sadece sayı girmelisiniz.')

    @staticmethod
    def eldeki_kadar_kelime_sorulacak(sorulacak_kelime_sayisi):
        print('{0} kelime sorulacak!'.format(sorulacak_kelime_sayisi))

    @staticmethod
    def cumle_kosulu_belirle():
        cumle_kosulu = input('Kelimelerin yanında cümle verilsin mi? (E/H) : ')
        print()
        return cumle_kosulu.strip()

    @staticmethod
    def cumle_yazdir(cumle):
        print(cumle)

    @staticmethod
    def kelimenin_anlamini_sor(kelime):
        anlam = input(kelime + ' : ')
        return anlam.strip()

    @staticmethod
    def yanit_dogru(anlam):
        print()
        print('Yanıt doğru!')
        print('[{0}]'.format(anlam))
        print()

    @staticmethod
    def dogru_sayisi_veritabaninda_arttirilamadi():
        print('Hata oluştu : Kelimenin doğru bilinme sayısı '
              'veritabanında arttırılamadı.')

    @staticmethod
    def yanit_yanlis(dogru_yanit):
        print()
        print('Yanıt yanlış!')
        print('Doğru yanıt {0} olacaktı.'.format(dogru_yanit))
        print()

    @staticmethod
    def dogru_sayisi_veritabaninda_azaltilamadi():
        print('Hata oluştu : Kelimenin doğru bilinme sayısı '
              'veritabanında azaltılamadı.')

    @staticmethod
    def sonucu_yazdir(sonuc):
        print('{0} sorudan {1} tanesine doğru {2} tanesine yanlış '
              'yanıt verdiniz!'.format(sonuc['soru_sayisi'],
                                       sonuc['dogru_sayisi'],
                                       sonuc['yanlis_sayisi']))


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
        self.__dogru_sayisi_kosulu = SoruSorIO.dogru_sayisi_kosulu_girisi()
        if not self.sorulacak_kelimenin_verilerini_hazirla():
            return
        if not self.sorulacak_kelime_sayisi_girisi():
            return
        self.cumle_kosulu_belirle()
        self.sorulacak_kelimeleri_belirle()
        self.sorulari_baslat()

    def sorulacak_kelimenin_verilerini_hazirla(self):
        veritabani = self.__veritabani
        dogru_sayisi_kosulu = self.__dogru_sayisi_kosulu
        kayitlar = veritabani.veritabanindan_kayit_getir(dogru_sayisi_kosulu)
        if self.kosula_uygun_kelime_bulundu_mu(kayitlar, dogru_sayisi_kosulu):
            return True
        return False

    def kosula_uygun_kelime_bulundu_mu(self, kayitlar, dogru_sayisi_kosulu):
        if kayitlar == []:
            SoruSorIO.kosula_uygun_kelime_bulunamadi(dogru_sayisi_kosulu)
            return False
        for kayit in kayitlar:
            self.__kelimeler.append(kayit.kelime)
            self.__anlamlar.append(kayit.anlam)
            self.__cumleler.append(kayit.cumle)
        return True

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
        toplam_kelime_sayisi = len(self.__kelimeler)
        kelime_sayisi = SoruSorIO.kelime_sayisi_girisi(toplam_kelime_sayisi)
        try:
            return int(kelime_sayisi)
        except ValueError:
            SoruSorIO.sadece_sayi_girmelisiniz()
            return ''

    def sorulacak_kelime_yok(self):
        if self.__sorulacak_kelime_sayisi <= 0:
            SoruSorIO.sorulacak_kelime_yok()
            return True
        return False

    def yeterince_kelime_mevcut_mu(self):
        if (self.__sorulacak_kelime_sayisi > len(self.__kelimeler)):
            self.__sorulacak_kelime_sayisi = len(self.__kelimeler)
            sorulacak_kelime_sayisi = self.__sorulacak_kelime_sayisi
            SoruSorIO.eldeki_kadar_kelime_sorulacak(sorulacak_kelime_sayisi)

    def cumle_kosulu_belirle(self):
        self.__cumle_kosulu = SoruSorIO.cumle_kosulu_belirle()

    def sorulacak_kelimeleri_belirle(self):
        for _ in range(0, self.__sorulacak_kelime_sayisi):
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
            anlam = SoruSorIO.kelimenin_anlamini_sor(kelime)
            self.yaniti_degerlendir(kelime, anlam)
        self.sonucu_yazdir()
        IO.menuye_don()

    def cumle_isteniyorsa_yazdir(self, kelime):
        cumle_kosulu = self.__cumle_kosulu
        cumleler = self.__cumleler
        kelimeler = self.__kelimeler
        if (cumle_kosulu == 'E' or cumle_kosulu == 'e'):
            SoruSorIO.cumle_yazdir(cumleler[kelimeler.index(kelime)])

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
        anlam = anlamlar[kelimeler.index(kelime)]
        SoruSorIO.yanit_dogru(anlam)

    def dogru_yanit_sayisini_arttir(self, kelime):
        veritabani = self.__veritabani
        if not veritabani.kaydin_dogru_sayisi_degerini_arttir(kelime):
            SoruSorIO.dogru_sayisi_veritabaninda_arttirilamadi()
        self.__dogru_yanit_sayisi += 1

    def yanit_yanlis(self, kelime):
        anlamlar = self.__anlamlar
        kelimeler = self.__kelimeler
        dogru_yanit = anlamlar[kelimeler.index(kelime)]
        SoruSorIO.yanit_yanlis(dogru_yanit)

    def dogru_yanit_sayisini_azalt(self, kelime):
        veritabani = self.__veritabani
        if not veritabani.kaydin_dogru_sayisi_degerini_azalt(kelime):
            SoruSorIO.dogru_sayisi_veritabaninda_azaltilamadi()
        self.__yanlis_yanit_sayisi += 1

    def sonucu_yazdir(self):
        soru_sayisi = self.__sorulacak_kelime_sayisi
        dogru_sayisi = self.__dogru_yanit_sayisi
        yanlis_sayisi = self.__yanlis_yanit_sayisi
        sonuc = {
            'soru_sayisi': soru_sayisi,
            'dogru_sayisi': dogru_sayisi,
            'yanlis_sayisi': yanlis_sayisi
            }
        SoruSorIO.sonucu_yazdir(sonuc)


class KelimeAnlamIO():
    @staticmethod
    def kelime_girisi():
        print()
        aranan = input('Anlamını öğrenmek istediğiniz kelimeyi giriniz : ')
        while (aranan.strip() == ''):
            aranan = input('Anlamını öğrenmek istediğiniz '
                           'kelimeyi girmelisiniz : ')
            print()
        return aranan.lower().strip()

    @staticmethod
    def veritabanindaki_kaydi_yazdir(kayit):
        print()
        print('# Veritabanındaki Kayıtlar #')
        print()
        print('Kelime : {0}'.format(kayit.kelime))
        print('Anlam : {0}'.format(kayit.anlam))
        print('Cümle : {0}'.format(kayit.cumle))

    @staticmethod
    def kelimenin_anlami_bulunamadi():
        print("Tureng'de belirttiğiniz kelimenin anlamı bulunamadı!")
        print()
        input('Menüye dönmek için ENTER tuşuna basın..')

    @staticmethod
    def tablo_basligini_yazdir(uzunluk):
        print()
        print()
        print('# Tureng Dictionary #')
        print()
        print('    Category' + 12 * ' ' + 'English' + 13 * ' ' + 'Turkish')
        print('------------' + 12 * '-' + '-------' + 13 * '-' + uzunluk * '-')

    @classmethod
    def tablo_satirlarini_yazdir(cls, kategoriler, kelimeler, anlam):
        for i in range(0, len(anlam)):
            cls.tablo_satirini_yazdir(i, kategoriler, kelimeler, anlam)

    @staticmethod
    def tablo_satirini_yazdir(index, kategoriler, kelimeler, anlam):
        i = index
        print(str(i + 1) + (4 - len(str(i+1))) * ' ', end='')
        print(kategoriler[i] + (20 - len(kategoriler[i])) * ' ', end='')
        print(kelimeler[i] + (20 - len(kelimeler[i])) * ' ', end='')
        print(anlam[i])
        if (i == 9 or i == 19 or i == 29 or i == 39 or i == 49 or i == 59):
            input("Devamı için [ENTER]'a basın")

    @staticmethod
    def veritabanina_eklensin_mi():
        print()
        eklensin_mi = input('Bulduğunuz kelime ve anlamları '
                            'veritabanına eklensin mi (E/H) ? : ')
        print()
        if (eklensin_mi == 'E' or eklensin_mi == 'e'):
            return True
        return False

    @staticmethod
    def eklenecek_anlamlar_girisi():
        eklenecek_anlamlar = ''
        while (eklenecek_anlamlar == ''):
            eklenecek_anlamlar = input('Eklemek istediğiniz kelimenin '
                                       'anlamlarının sıra numaralarını '
                                       'virgülle ayırarak giriniz : ')
        return eklenecek_anlamlar

    @staticmethod
    def yanlis_deger_girdiniz():
        print('Yanlış değer girdiniz!')
        print()

    @staticmethod
    def yanlis_sira_numarasi_girdiniz():
        print('Yanlış sıra numarası girdiniz!')
        print()

    @staticmethod
    def eklenecek_anlamlari_yazdir(eklenecek_anlamlar):
        print()
        print('Eklenecek anlamlar :', eklenecek_anlamlar)
        print()

    @staticmethod
    def cumle_girisi():
        cumle = input('Kelimenin içinde geçtiği bir cümle giriniz '
                      '(İsteğe bağlı) : ')
        print()
        return cumle

    @staticmethod
    def veritabanina_eklendi():
        print()
        print('Veritabanına eklendi.')
        print()
        IO.menuye_don()

    @staticmethod
    def veritabanina_eklenirken_hata():
        print()
        print('Hata : Veritabanına eklenemedi.')
        print()
        IO.menuye_don()


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
        self.__kelime = KelimeAnlamIO.kelime_girisi()
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

    def kelime_veritabaninda_mevcutsa_yazdir(self, kelime):
        veritabani = self.__veritabani
        kayit = veritabani.kelimenin_kaydini_getir(kelime)
        if kayit is not None:
            self.__kelime_mevcudiyet = True
            KelimeAnlamIO.veritabanindaki_kaydi_yazdir(kayit)

    def sayfayi_getir(self):
        try:
            page = requests.get('http://tureng.com/en/turkish-english/{0}'
                                .format(self.__kelime,))
            return page
        except NameError:
            IO.requests_kutuphanesi_eksik()
            return None

    def parse_edilmis_html_verisini_getir(self):
        try:
            tree = html.fromstring(self.__page.content)
            return tree
        except NameError:
            IO.lxml_kutuphanesi_eksik()
            return None

    def kelimeye_ait_bulunan_verileri_al(self):
        kelimeler, anlamlar = self.verileri_ayikla()
        if (len(anlamlar) == 0 or ((self.__kelime in anlamlar) and
                                   self.__kelime not in kelimeler)):
            KelimeAnlamIO.kelimenin_anlami_bulunamadi()
            return False
        return True

    def verileri_ayikla(self):
        tree = self.__tree
        self.__kategoriler = tree.xpath('//td[@class="hidden-xs"]/text()')
        self.__kelimeler = tree.xpath('//td[@class="en tm"]/a/text()')
        self.__anlamlar = tree.xpath('//td[@class="tr ts"]/a/text()')
        return self.__kelimeler, self.__anlamlar

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
        KelimeAnlamIO.tablo_basligini_yazdir(self.__euaksu)
        kategoriler = self.__kategoriler
        kelimeler = self.__kelimeler
        anlam = self.__anlam
        KelimeAnlamIO.tablo_satirlarini_yazdir(kategoriler, kelimeler, anlam)

    def kelime_mevcut_mu(self):
        if self.__kelime_mevcudiyet:
            print()
            IO.menuye_don()
        return self.__kelime_mevcudiyet

    def veritabanina_eklensin_mi(self):
        if KelimeAnlamIO.veritabanina_eklensin_mi():
            self.veritabanina_ekle()
            return True
        IO.menuye_don()
        return False

    def veritabanina_ekle(self):
        sira_numaralari = self.sira_numaralarini_hazirla()
        while (self.sira_numaralari_kontrol(sira_numaralari) is False):
            sira_numaralari = self.sira_numaralarini_hazirla()
        self.secilenleri_veritabanina_kaydet(sira_numaralari)

    def sira_numaralarini_hazirla(self):
        eklenecek_anlamlar = KelimeAnlamIO.eklenecek_anlamlar_girisi()
        eklenecek_anlamlar = self.bosluklari_sil(eklenecek_anlamlar)
        return self.virgule_gore_ayirarak_listele(eklenecek_anlamlar)

    def bosluklari_sil(self, eklenecek_anlamlar):
        return ''.join(eklenecek_anlamlar.split())

    def virgule_gore_ayirarak_listele(self, eklenecek_anlamlar):
        return eklenecek_anlamlar.split(',')

    def sira_numaralari_kontrol(self, sira_numaralari):
        for i in sira_numaralari:
            if not i.isdigit():
                KelimeAnlamIO.yanlis_deger_girdiniz()
                return False
            elif int(i) <= 0 or int(i) > len(self.__anlam):
                KelimeAnlamIO.yanlis_sira_numarasi_girdiniz()
                return False
        return True

    def secilenleri_veritabanina_kaydet(self, sira_numaralari):
        kelime_verisi = self.kelime_verisini_hazirla(sira_numaralari)
        if self.__veritabani.veritabanina_ekle(kelime_verisi):
            KelimeAnlamIO.veritabanina_eklendi()
        else:
            KelimeAnlamIO.veritabanina_eklenirken_hata()

    def kelime_verisini_hazirla(self, sira_numaralari):
        eklenecek_anlamlar = self.eklenecek_anlamlari_hazirla(sira_numaralari)
        KelimeAnlamIO.eklenecek_anlamlari_yazdir(eklenecek_anlamlar)
        cumle = KelimeAnlamIO.cumle_girisi()
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


def kucuk_harfe_cevir(metin):
    lower_map = {
        ord('I'): 'ı',
        ord('İ'): 'i'
        }
    metin = metin.translate(lower_map).lower()
    return metin


if __name__ == '__main__':
    VeritabaniIslemleri().veritabanini_hazirla()
    Menu().menu_secim()
