#!/usr/bin/python3

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import UnmappedInstanceError
import random
import os
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

def menu():
    secim = 0
    while (secim != 6):
        clear_screen()
        print(
  '''
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

  '''
        )
        secim = input('Seçiminiz : ')
        while secim.isdigit() == False or (int(secim) not in range(1, 7)):
            print() # new line
            print('Menüde yapmak istediğiniz işlemin ',
                  'solunda kalan sayıyı girin.')
            secim = input('Seçiminiz : ')
        secim = int(secim)
        if (secim == 1):
            kelime_ekle()
        elif (secim == 2):
            kelime_guncelle()
        elif (secim == 3):
            kelime_sil()
        elif (secim == 4):
            soru_sor()
        elif (secim == 5):
            kelime_anlam()
        elif (secim == 6):
        	pass
        else:
            print() # new line
            print('Yanlış seçim!')
            print() # new line


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')


def kelime_ekle():
    kelime = input('Kelimeyi giriniz : ')
    while (kelime == ''):
        kelime = input('İngilizce kelimeyi girmelisiniz : ')
    for row in session.query(Kelimeler.kelime).all():
        if (row.kelime == kelime):
            print('Bu kelime zaten veritabanında mevcut.')
            input('Menüye dönmek için ENTER tuşuna basın..')
            return
    anlam = input('Kelimenin anlamını giriniz : ')
    while (anlam == ''):
        anlam = input('Kelimenin anlamını girmelisiniz : ')
    cumle = input('Kelimenin içinde bulunduğu cümleyi giriniz ' \
                  '(İsteğe bağlı) : ')
    kelime = Kelimeler(kelime=kelime, anlam=anlam, cumle=cumle, dogru_sayisi=0)
    session.add(kelime)
    session.commit()
    print() # new line
    print('Veritabanına eklendi.')
    print() # new line
    input('Menüye dönmek için ENTER tuşuna basın..')


def kelime_guncelle():
    kelime = input('Güncellenecek kelimeyi giriniz : ')
    while (kelime == ''):
        kelime = input('Güncellenecek kelimeyi girmelisiniz : ')
    kelime_mevcudiyet = False
    for row in session.query(Kelimeler.kelime).all():
        if (row.kelime == kelime):
            kelime_mevcudiyet = True
    if (kelime_mevcudiyet == False):
        print() # new line
        print('Güncellemek istediğiniz kelime veritabanında mevcut değil!')
        print() # new line
        input('Menüye dönmek için ENTER tuşuna basın..')
        return
    yeni_kelime = input('Yeni kelimeyi giriniz : ')
    while (yeni_kelime == ''):
        yeni_kelime = input('Yeni kelimeyi girmelisiniz : ')
    yeni_kelime_mevcudiyet = False
    for row in session.query(Kelimeler.kelime).all():
        if (row.kelime != kelime and row.kelime == yeni_kelime):
            print('Güncellemek üzere yazdığınız yeni kelime',
                  'zaten veritabanında mevcut')
            input('Menüye dönmek için ENTER tuşuna basın..')
            return
    anlam = input('Yeni kelimenin anlamını giriniz : ')
    while (anlam == ''):
        anlam = input('Yeni kelimenin anlamını girmelisiniz : ')
    cumle = input('Yeni kelimenin içinde bulunduğu cümleyi giriniz : ')
    record = session.query(Kelimeler).filter_by(kelime=kelime).first()
    record.kelime = yeni_kelime
    record.anlam = anlam
    record.cumle = cumle
    session.commit()

    print() # new line
    print("Veritabanında güncellendi.")
    print() # new line
    input('Menüye dönmek için ENTER tuşuna basın..')


def kelime_sil():
    print()
    kelime = input('Silinecek kelimeyi giriniz : ')
    while (kelime == ''):
        print()
        kelime = input('Silinecek kelimeyi girmelisiniz : ')
    try:
        silinecek_kelime = session.query(Kelimeler) \
                           .filter_by(kelime=kelime).first()
        session.delete(silinecek_kelime)
        session.commit()
        print() # new line
        print("Veritabanından silindi.")
        print() # new line
    except UnmappedInstanceError:
        print() # new line
        print('Silmek istediğiniz kelime kayıtlı değil!')
        print() # new line
    input('Menüye dönmek için ENTER tuşuna basın..')


def soru_sor():
    kelimeler = []
    anlamlar = []
    cumleler = []
    sorulacak_kelimeler = []
    sorulacak_kelime_sayisi = ''
    dogru_sayisi_kosulu = ''
    dogru_yanit_sayisi = 0
    yanlis_yanit_sayisi = 0

    print() # new line
    while (dogru_sayisi_kosulu == ''):
        try:
            dogru_sayisi_kosulu = input('Doğru bilinme sayısı ' \
                                        'kaçtan az olan kelimeler sorulsun? : ')
            dogru_sayisi_kosulu = int(dogru_sayisi_kosulu)
        except ValueError:
            print('Sadece sayı girmelisiniz.')
            dogru_sayisi_kosulu = ''
            continue
    for row in session.query(Kelimeler) \
               .filter(Kelimeler.dogru_sayisi < dogru_sayisi_kosulu).all():
        kelimeler.append(row.kelime)
        anlamlar.append(row.anlam)
        cumleler.append(row.cumle)

    if len(kelimeler) == 0:
        print('{0} sayısından daha az doğru sayısına ' \
              'sahip kelime bulunamadı.'.format(dogru_sayisi_kosulu))
        print()
        input('Menüye dönmek için ENTER tuşuna basın..')
        return

    print() # new line
    while (sorulacak_kelime_sayisi == ''):
        try:
            sorulacak_kelime_sayisi = input \
                                      (
                                      '{0} kelimeden kaçı sorulsun? : ' \
                                      .format(len(kelimeler))
                                      )
            sorulacak_kelime_sayisi = int(sorulacak_kelime_sayisi)
            if sorulacak_kelime_sayisi <= 0:
                print() # new line
                input('Menüye dönmek için ENTER tuşuna basın..')
                return
        except ValueError:
            print('Sadece sayı girmelisiniz.')
            sorulacak_kelime_sayisi = ''
            continue
    if (sorulacak_kelime_sayisi > len(kelimeler)):
        sorulacak_kelime_sayisi = len(kelimeler)
        print('{0} kelime sorulacak!'.format(sorulacak_kelime_sayisi))
    cumle_kosulu = input('Kelimelerin yanında cümle verilsin mi? (E/H) : ')
    print() # new line

    for i in range(0, sorulacak_kelime_sayisi):
        sorulacak_kelime = kelimeler[random.randrange(0, len(kelimeler))]
        while (sorulacak_kelime in sorulacak_kelimeler):
            sorulacak_kelime = kelimeler[random.randrange(0, len(kelimeler))]
        sorulacak_kelimeler.append(sorulacak_kelime)
    for i in sorulacak_kelimeler:
        if (cumle_kosulu == 'E' or cumle_kosulu == 'e'):
            print(cumleler[kelimeler.index(i)])
        anlam = input(i + ' : ')
        if (anlam in anlamlar[kelimeler.index(i)] and anlam.strip() != ''):
            print() # new line
            print('Yanıt doğru!')
            print('[' + anlamlar[kelimeler.index(i)] + ']')
            print() # new line
            record = session.query(Kelimeler) \
                     .filter(Kelimeler.kelime == i).first()
            record.dogru_sayisi += 1
            session.commit()
            dogru_yanit_sayisi += 1
        else:
            print() # new line
            print('Yanıt yanlış!')
            print('Doğru yanıt {0} olacaktı.' \
                  .format(anlamlar[kelimeler.index(i)]))
            print() # new line
            record = session.query(Kelimeler) \
                     .filter(Kelimeler.kelime == i).first()
            record.dogru_sayisi -= 1
            session.commit()
            yanlis_yanit_sayisi += 1
    print('{0} sorudan {1} tanesine doğru {2} tanesine yanlış ' \
          'yanıt verdiniz!'.format(sorulacak_kelime_sayisi,
                                   dogru_yanit_sayisi,
                                   yanlis_yanit_sayisi)
         )
    input('Menüye dönmek için ENTER tuşuna basın..')


def kelime_anlam():
    print()
    aranan = input('Anlamını öğrenmek istediğiniz kelimeyi giriniz : ')
    page = None
    tree = None
    while (aranan == ''):
        aranan = input('Anlamını öğrenmek istediğiniz kelimeyi girmelisiniz : ')
        print()
    kelime_mevcudiyet = False
    for row in session.query(Kelimeler).all():
        if (row.kelime == aranan):
            kelime_mevcudiyet = True
            print() # new line
            print('# Veritabanındaki Kayıtlar #')
            print() # new line
            print('Kelime : {0}'.format(row.kelime))
            print('Anlam : {0}'.format(row.anlam))
            print('Cümle : {0}'.format(row.cumle))
    print()
    try:
        page = requests.get('http://tureng.com/en/turkish-english/{0}' \
               .format(aranan,))
    except NameError:
        print() # new line
        print('requests kütüphanesini yüklemelisiniz!')
        print('[python -m pip install requests]')
        print() # new line
        input('Menüye dönmek için ENTER tuşuna basın..')
        return
    try:
        tree = html.fromstring(page.content)
    except NameError:
        print() # new line
        print('lxml kütüphanesini yüklemelisiniz!')
        print('[python -m pip install lxml]')
        print() # new line
        input('Menüye dönmek için ENTER tuşuna basın..')
        return

    kategori = tree.xpath('//td[@class="hidden-xs"]/text()')
    kelimeler = tree.xpath('//td[@class="en tm"]/a/text()')
    anlamlar = tree.xpath('//td[@class="tr ts"]/a/text()')
    if (len(anlamlar) == 0 or ((aranan in anlamlar) and \
                                aranan not in kelimeler)):
        print("Tureng'de belirttiğiniz kelimenin anlamı bulunamadı!")
        print() # new line
        input('Menüye dönmek için ENTER tuşuna basın..')
        return

    anlam = []
    euaksu = 0 # euaksu = en_uzun_anlamin_karakter_sayisi_uzunlugu
    for i in range(0, len(kelimeler)):
        if (kelimeler[i] == aranan and anlamlar[i] not in anlam):
            anlam.append(anlamlar[i])
            euaksu = len(anlamlar[i]) if len(anlamlar[i]) > euaksu else euaksu

    print() # new line
    print('# Tureng Dictionary #')
    print() # new line
    print('    Category' + 12 * ' ' + 'English' + 13 * ' ' + 'Turkish')
    print('------------' + 12 * '-' + '-------' + 13 * '-' + euaksu * '-')
    for i in range(0, len(anlam)):
        print(str(i+1) + (4 - len(str(i+1))) * ' ' + \
              kategori[i] + (20 - len(kategori[i])) * ' ', end='')
        print(kelimeler[i] + (20 - len(kelimeler[i])) * ' ', end='')
        print(anlam[i])
        if (i == 9 or i == 19 or i == 29 or i == 39 or i == 49 or i == 59):
        	daha_fazla = input("Devamı için [ENTER]'a basın")
    if (kelime_mevcudiyet == False):
        print() # new line
        eklensin_mi = input('Bulduğunuz kelime ve anlamları ' \
                            'veritabanına eklensin mi (E/H) ? : ')
        print() # new line
        if (eklensin_mi == 'E' or eklensin_mi == 'e'):
            eklenecek_anlamlar = ''
            sira_numaralari = []
            while (eklenecek_anlamlar == ''):
                eklenecek_anlamlar = input('Eklemek istediğiniz kelimenin ' \
                                            'anlamlarının sıra numaralarını ' \
                                            'virgülle ayırarak giriniz : ')
                sira_numaralari = (''.join(eklenecek_anlamlar.split())) \
                                  .split(',')
                for i in sira_numaralari:
                    if not i.isdigit():
                        eklenecek_anlamlar = ''
                        print('Yanlış değer girdiniz!')
                        print()
                        break
                    elif int(i) <= 0 or int(i) > len(anlam):
                        eklenecek_anlamlar = ''
                        print('Yanlış sıra numarası girdiniz!')
                        print()
                        break
            eklenecek_anlamlar = []
            print()
            for i in sira_numaralari:
                if anlam[int(i) - 1] in anlam:
                    eklenecek_anlamlar.append(anlam[int(i) - 1])
            eklenecek_anlamlar = ', '.join(eklenecek_anlamlar)
            print('Eklenecek anlamlar :', eklenecek_anlamlar)
            print() # new line
            cumle = input('Kelimenin içinde geçtiği bir cümle giriniz ' \
                          '(İsteğe bağlı) : ')
            print() # new line
            record = Kelimeler(kelime=aranan, anlam=eklenecek_anlamlar, \
                               cumle=cumle, dogru_sayisi=0)
            session.add(record)
            session.commit()
            print() # new line
            print('Veritabanına eklendi.')
            print() # new line
    else:
        print() # new line
    input('Menüye dönmek için ENTER tuşuna basın..')

menu()
