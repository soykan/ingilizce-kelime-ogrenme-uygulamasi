#!/usr/bin/python3

import sqlite3
import random
try:
    from lxml import html
except ImportError:
    print(
        'Programın bazı fonksiyonlarından yararlanabilmek için lxml',
        'kütüphanesini yüklemeniz gerekiyor.'
        )
    print('[python -m pip install lxml]')
try:
    import requests
except ImportError:
    print(
        'Programın bazı fonksiyonlarından yararlanabilmek için requests',
        'kütüphanesini yüklemeniz gerekiyor.'
        )
    print('[python -m pip install requests]')


def menu():
    secim = 0
    while (secim != 6):
        print('Menü')
        print('1.Kelime ekle')
        print('2.Kelime güncelle')
        print('3.Kelime sil')
        print('4.Soru sor')
        print('5.Kelime anlamı sorgula')
        print('6.Çıkış')
        secim = input('Seçiminiz : ')
        while (secim.isdigit() == False):
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
            print('') # new line
            print('Yanlış seçim!')
            print('') # new line


def kelime_ekle():
    kelime = input('Kelimeyi giriniz : ')
    while (kelime == ''):
        kelime = input('İngilizce kelimeyi girmelisiniz : ')
    conn = sqlite3.connect('kelime-veritabani.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kelimeler
                (kelime text NOT NULL, anlam text NOT NULL, cumle text,
                dogru_sayisi integer NOT NULL)''')
    c.execute('SELECT * FROM kelimeler')
    for row in c:
        if (row[0] == kelime):
            print('Bu kelime zaten veritabanında mevcut.')
            conn.close()
            return
    anlam = input('Kelimenin anlamını giriniz : ')
    while (anlam == ''):
        anlam = input('Kelimenin anlamını girmelisiniz : ')
    cumle = input('Kelimenin içinde bulunduğu cümleyi giriniz (İsteğe bağlı) : ')
    conn = sqlite3.connect('kelime-veritabani.db')
    c = conn.cursor()
    c.execute('INSERT INTO kelimeler VALUES (?, ?, ?, ?)', (kelime, anlam, cumle, 0))
    conn.commit()
    conn.close()
    print('') # new line
    print("Veritabanına eklendi.")
    print('') # new line


def kelime_guncelle():
    kelime = input('Güncellenecek kelimeyi giriniz : ')
    while (kelime == ''):
        kelime = input('Güncellenecek kelimeyi girmelisiniz : ')
    conn = sqlite3.connect('kelime-veritabani.db')
    c = conn.cursor()
    c.execute('SELECT * FROM kelimeler')
    kelime_mevcudiyet = False
    for row in c:
        if (row[0] == kelime):
            kelime_mevcudiyet = True
    if (kelime_mevcudiyet == False):
        print('Güncellemek istediğiniz kelime veritabanında mevcut değil!')
        conn.close()
        return
    yeni_kelime = input('Yeni kelimeyi giriniz : ')
    while (yeni_kelime == ''):
        yeni_kelime = input('Yeni kelimeyi girmelisiniz : ')
    c.execute('SELECT * FROM kelimeler')
    yeni_kelime_mevcudiyet = False
    for row in c:
        if (row[0] != kelime and row[0] == yeni_kelime):
            print('Güncellemek üzere yazdığınız yeni kelime',
                'zaten veritabanında mevcut')
            conn.close()
            return
    anlam = input('Yeni kelimenin anlamını giriniz : ')
    while (anlam == ''):
        anlam = input('Yeni kelimenin anlamını girmelisiniz : ')
    cumle = input('Yeni kelimenin içinde bulunduğu cümleyi giriniz : ')
    c.execute('''UPDATE kelimeler SET kelime = ?, anlam = ?, cumle = ?
                WHERE kelime = ?''', (yeni_kelime, anlam, cumle, kelime))
    conn.commit()
    conn.close()
    print('') # new line
    print("Veritabanında güncellendi.")
    print('') # new line


def kelime_sil():
    kelime = input('Silinecek kelimeyi giriniz : ')
    while (kelime == ''):
        kelime = input('Silinecek kelimeyi girmelisiniz : ')
    conn = sqlite3.connect('kelime-veritabani.db')
    c = conn.cursor()
    c.execute('SELECT * FROM kelimeler')
    kelime_mevcudiyet = False
    for row in c:
        if (kelime == row[0]):
            kelime_mevcudiyet = True
            c.execute('DELETE FROM kelimeler WHERE kelime = ?', (kelime,))
            conn.commit()
            print('') # new line
            print("Veritabanından silindi.")
            print('') # new line
            break
    if (kelime_mevcudiyet == False):
        print('Silmek istediğiniz kelime veritabanında mevcut değil!')
    conn.close()



def soru_sor():
    kelimeler = []
    anlamlar = []
    cumleler = []
    sorulacak_kelimeler = []
    sorulacak_kelime_sayisi = ''
    dogru_sayisi_kosulu = ''
    dogru_yanit_sayisi = 0
    yanlis_yanit_sayisi = 0

    print('') # new line
    while (dogru_sayisi_kosulu == ''):
        try:
            dogru_sayisi_kosulu = input('Doğru bilinme sayısı kaçtan az olan kelimeler sorulsun? : ')
            dogru_sayisi_kosulu = int(dogru_sayisi_kosulu)
        except ValueError:
            print('Sadece sayı girmelisiniz.')
            dogru_sayisi_kosulu = ''
            continue

    conn = sqlite3.connect('kelime-veritabani.db')
    c = conn.cursor()
    c.execute('SELECT * FROM kelimeler WHERE dogru_sayisi < ?', (dogru_sayisi_kosulu,))
    for row in c:
        kelimeler.append(row[0])
        anlamlar.append(row[1])
        cumleler.append(row[2])
    conn.close()

    print('') # new line
    while (sorulacak_kelime_sayisi == ''):
        try:
            sorulacak_kelime_sayisi = input('{0} kelimeden kaçı sorulsun? : '.format(len(kelimeler)))
            sorulacak_kelime_sayisi = int(sorulacak_kelime_sayisi)
        except ValueError:
            print('Sadece sayı girmelisiniz.')
            sorulacak_kelime_sayisi = ''
            continue
    if (sorulacak_kelime_sayisi > len(kelimeler)):
        sorulacak_kelime_sayisi = len(kelimeler)
        print('{0} kelime sorulacak!'.format(sorulacak_kelime_sayisi))
    cumle_kosulu = input('Kelimelerin yanında cümle verilsin mi? (E/H) : ')
    print('') # new line

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
            print('') # new line
            print('Yanıt doğru!')
            print('[' + anlamlar[kelimeler.index(i)] + ']')
            print('') # new line
            conn = sqlite3.connect('kelime-veritabani.db')
            c = conn.cursor()
            c.execute('UPDATE kelimeler SET dogru_sayisi = dogru_sayisi + 1 WHERE kelime = ?', (i,))
            conn.commit()
            conn.close()
            dogru_yanit_sayisi += 1
        else:
            print('') # new line
            print('Yanıt yanlış!')
            print('Doğru yanıt {0} olacaktı.'.format(anlamlar[kelimeler.index(i)]))
            print('') # new line
            conn = sqlite3.connect('kelime-veritabani.db')
            c = conn.cursor()
            c.execute('UPDATE kelimeler SET dogru_sayisi = dogru_sayisi - 1 WHERE kelime = ?', (i,))
            conn.commit()
            conn.close()
            yanlis_yanit_sayisi += 1
    print('''{0} sorudan {1} tanesine doğru {2} tanesine yanlış yanıt verdiniz!
            '''.format(sorulacak_kelime_sayisi, dogru_yanit_sayisi, yanlis_yanit_sayisi))

def kelime_anlam():
    aranan = input('Anlamını öğrenmek istediğiniz kelimeyi giriniz : ')
    page = None
    tree = None
    while (aranan == ''):
        aranan = input('Anlamını öğrenmek istediğiniz kelimeyi girmelisiniz : ')
    conn = sqlite3.connect('kelime-veritabani.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kelimeler
                (kelime text NOT NULL, anlam text NOT NULL, cumle text,
                dogru_sayisi integer NOT NULL)''')
    c.execute('SELECT * FROM kelimeler')
    kelime_mevcudiyet = False
    for row in c:
        if (row[0] == aranan):
            kelime_mevcudiyet = True
            print('') # new line
            print('| -- Veritabanındaki Kayıtlar -- |')
            print('Kelime : {0}'.format(row[0]))
            print('Anlam : {0}'.format(row[1]))
            print('Cümle : {0}'.format(row[2]))
    conn.close()
    try:
        page = requests.get('http://tureng.com/en/turkish-english/{0}'.format(aranan,))
    except NameError:
        print('') # new line
        print('requests kütüphanesini yüklemelisiniz!')
        print('[python -m pip install requests]')
        print('') # new line
        return
    try:
        tree = html.fromstring(page.content)
    except NameError:
        print('') # new line
        print('lxml kütüphanesini yüklemelisiniz!')
        print('[python -m pip install lxml]')
        print('') # new line
        return

    kategori = tree.xpath('//td[@class="hidden-xs"]/text()')
    kelimeler = tree.xpath('//td[@class="en tm"]/a/text()')
    anlamlar = tree.xpath('//td[@class="tr ts"]/a/text()')

    anlam = []
    for i in range(0, len(kelimeler)):
        if (kelimeler[i] == aranan and anlamlar[i] not in anlam):
            anlam.append(anlamlar[i])

    print('') # new line
    print('| -- Tureng -- |')
    print('    Category' + 12 * ' ' + 'English' + 13 * ' ' + 'Turkish')
    print('----------------------------------------------------------')
    for i in range(0, len(anlam)):
        print(str(i+1) + (4 - len(str(i+1))) * ' ' + kategori[i] + (20 - len(kategori[i])) * ' ', end='')
        print(kelimeler[i] + (20 - len(kelimeler[i])) * ' ', end='')
        print(anlam[i])
        if (i == 9 or i == 19 or i == 29 or i == 39 or i == 49 or i == 59):
        	daha_fazla = input('Devamı için [ENTER]\'a basın')
    if (kelime_mevcudiyet == False):
        eklensin_mi = input('Bulduğunuz kelime ve anlamları veritabanına eklensin mi (E/H) ? : ')
        if (eklensin_mi == 'E' or eklensin_mi == 'e'):
            eklenecek_anlamlar = input('Eklemek istediğiniz kelimenin anlamlarının '
                                        + 'sıra numaralarını virgülle ayırarak ' +
                                        'giriniz : ')
            sira_numaralari = (''.join(eklenecek_anlamlar.split())).split(',')
            eklenecek_anlamlar = []
            for i in sira_numaralari:
                eklenecek_anlamlar.append(anlam[int(i) - 1])
            eklenecek_anlamlar = ', '.join(eklenecek_anlamlar)
            print('Eklenecek anlamlar :', eklenecek_anlamlar)
            cumle = input('Kelimenin içinde geçtiği bir cümle giriniz (İsteğe bağlı) : ')
            conn = sqlite3.connect('kelime-veritabani.db')
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS kelimeler
                        (kelime text NOT NULL, anlam text NOT NULL, cumle text,
                        dogru_sayisi integer NOT NULL)''')
            c.execute('INSERT INTO kelimeler VALUES (?, ?, ?, ?)', (aranan, eklenecek_anlamlar, cumle, 0))
            conn.commit()
            conn.close()

menu()
