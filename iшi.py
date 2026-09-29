from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey ,X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF,HKDFExpand
from cryptography.hazmat.primitives.asymmetric import ec , x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes,hmac
from urllib.parse import to_bytes
from os import urandom
from control import *
import tkinter as tk
import urllib.parse
import hashlib
import codecs
import os

"""
Если вы вдруг нашли мой проект и решили его прочесть, то выражаю вам свои благодарность.
Если вы достаточно компитентны чтобы оценить мой код и указать ошибки(о которых я не писал), пожалуйста сделайте это
Оба файла я писал где-то неделю или полторы в 10 классе перед пересдачей инд. проекта.
Пытался сделать всё как можно более приближённым к реальному протоколу aesgcm в tls 1.3,но вышло так ,как вы скоро увидете
Программа создана для экстремистского мессенджера Telegram(win11)(хотя по сути её можно использовать в любом мессенджере, просто тогда надо будет вводить всё вручную)
Хотя вообще ,изначально, я делал её для макса ,чтобы сообщения не могли прочитать.
Однако, устанавливать себе на комп вредоносное по я не хотел,поэтому сделал для тг. 
Для правильной авто отправки сообщений в тг необходимо указать ваш размер интерфейся в % чуть ниже
"""





Pid = findPid()

cl_hand_key = b''
cl_hand_iv = b''
peer_hand_iv = b''
peer_hand_key = b''
hand_key = b''

seq_num = 0
cil = 12 #cipher_iv_length
ckl = 32 #cipher_key_length
hsh2 = hashes.SHA256()
hsh3 = hashes.SHA384()

screenWidth, screenHeight = pyautogui.size()
ratio = screenWidth/screenHeight
pourcent = 125 # <--------------------------------------------- Вот тут
meslen = round(50 * (pourcent/100))

def dtext(txt,y,y2,x = None,x2 = None,txt2 = 'Подтвердить',func = None): #Показать окно с текстом
    window = tk.Tk()
    window.title("AEC")  # AEC - Addiotional Elleptic Crypthography
    window.geometry('800x450')
    text = tk.Label(window, text=txt)
    text.pack(pady=y,padx=x)
    try:
        button = tk.Button(window, bd = 5, text = txt2, command = lambda : (window.destroy(),func()))
    except:
        print(1)
    button.pack(pady=y2,padx=x2)
    window.mainloop()

def main(clkey,cliv,pkey,piv): #как можно заметить в этой функции при шифровании и дешифровке используются одни и те же пары key и iv ,что категорически запрещено
    window = tk.Tk() #"поменять" всмысле потом сделать правильные key и iv
    window.title("SEC")
    window.geometry('800x450')
    entext = tk.Label(window, text = 'Зашифровать и отправить')
    entext.place(x = 55, y = 70)
    detext = tk.Label(window, text = 'Расшифровать сообщения')
    detext.place(x = 550, y = 20)
    f = tk.Text(window, height = 5, width = 22)
    f.place(x = 40, y = 120)#поменять \/
    send = tk.Button(window,width = 15 , height = 1,bd = 5,command = lambda : (crypt(f.get('1.0',tk.END),pkey,piv),f.delete('1.0',tk.END)),text = 'Отправить')
    send.place(x = 80, y = 255)
    dec = tk.Button(window,width = 20 , height = 2,bd = 3,command = lambda : decrypted(readt(Pid, 1)[1],pkey,piv),text = 'Прочитать \nпоследнее сообщение')
    ent = tk.Entry(window,width = 5)
    ent.place(x = 670, y = 173)
    dec.place(x = 560, y = 70)
    decn = tk.Button(window,width = 10, height = 1, bd = 3,command = lambda : (print(manual.get('1.0',tk.END)),decrypted(readt(Pid, int(manual.get('1.0',tk.END)))[1],pkey,piv),ent.delete(0, tk.END)),text = 'Прочитать') #тут юзер вводит n сообщений для чтения, не работало , не было времени разбираться
    decn.place(x = 560, y = 160)
    txt1 = tk.Label(window,text = 'сообщений')
    txt1.place(x = 560 , y = 200)
    txt2 = tk.Label(window,text = 'Ввести сообщения\nвручную:') #не работало =(
    txt2.place(x = 560 , y = 240)
    manual = tk.Text(window, height = 5, width = 15)
    manual.place(x = 554 , y = 300)
    manbutt = tk.Button(window,width = 6, height = 3, bd = 3, text = 'Прочи\nтать',command = lambda : (decrypted(manual.get('1.0',tk.END),pkey,piv),manual.delete('1.0',tk.END)))
    manbutt.place(x = 725 , y = 310)
    window.mainloop()

def decrypted(mess,key,iv, n = 0): #Вывод дешифрованного сообщения в отдельном окне
    norm_mess = decrypt(n,key,iv,mss = mess)[0]
    decwin = tk.Tk()
    decwin.title("SEC")
    decwin.geometry('200x200')
    text = tk.Label(decwin,text = norm_mess)
    text.place(x = 0, y = 0)

#сф - стандартная фунция tls 1.3

def hkdf_expand_label(secret: bytes, label: bytes, context: bytes, length: bytes) -> bytes: #сф
    """
    (Вспомогательная функция. Определена в RFC 8446 (раздел 7.1))
    """
    hkdf_label = (
        length.to_bytes(2, 'big') +
        # Внимание: строка b'tls13 ' с пробелом!
        encode_vector(1, b'tls13 ' + label) +
        encode_vector(1, context)
    )
    hkdf = HKDFExpand(
        algorithm=hashes.SHA384(),
        length=length,
        info=hkdf_label,
    )
    return hkdf.derive(secret)

def encode_vector(length_bytes_count: int, content: bytes): #сф
    """
    Кодирует поле переменной длины, как принято в TLS
    (приписывает в начале длину).
    """
    return len(content).to_bytes(length_bytes_count, 'big') + content

def hkdf_extract(salt: bytes, input_key_material: bytes) -> bytes: #сф
    """
    (Реализует первую половину алгоритма HKDF (RFC 5869))
    """
    hm = hmac.HMAC(salt, hsh3)
    hm.update(input_key_material)
    return hm.finalize()

def get_data(mode,hdata): #эта функция преобразует скопированный текст из readt()(control) в читаемый для cryptography
    if mode == 3:
        blist = ['к','кц','с','сц']
        inc = []
        for x in blist:
            inc.append(hdata.find(x))
        ppk = codecs.decode(hdata[inc[0] + 3:inc[1] - 1],'unicode_escape').encode('latin1')
        ps = codecs.decode(hdata[inc[2] + 3:inc[3] - 1],'unicode_escape').encode('latin1')
        return ppk, ps
    if mode == 2:
        mess = []
        substring = "б"
        inc = []
        start = 0
        while True:
            start = hdata.find(substring, start)
            if start == -1: break
            inc.append(start)
            start += len(substring)
        for x in range(0, len(inc), 2):
            mess.append(codecs.decode(hdata[inc[x] + 3:inc[x + 1] - 1],'unicode_escape').encode('latin1'))
        return mess

def handshake(): #хендшейк пользователей, почти автоматизированный
    global seq_num
    global hand_key
    global peer_hand_key
    global peer_hand_iv
    global cl_hand_iv
    global cl_hand_key
    #Клиент
    cl_private_key = X25519PrivateKey.generate() #Наш секрет
    cl_pub_key = cl_private_key.public_key() #Наш паб
    wtext('к' + str(cl_pub_key.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)) + 'кц',Pid)
    cl_salt = os.urandom(32) #это нужно передать
    wtext('с' + str(cl_salt) + 'сц', Pid) # символы к,кц,с,сц я добавил для упрощения дальщейго выделения нужного текста в get_data() (возможно так делать нельзя)

    #Пиир
    dtext('Теперь подтвердите ,что вы получили два аналогичных сообщения от собеседника',150,20,func = print())
    #Перед тем как брать данные от пира необходимо сделать подтвержение от пользователя ,что сообщения пришли
    #29.09.26 надо бы как-нибудь сделать чтобы пользователь мог выбрать отсылает он сообщения первым или получает
    peer_pub_key , peer_salt = get_data(3,readt(findPid(), 2)[1])
    #Общий секрет
    try:
        cl_shared_key = cl_private_key.exchange(X25519PublicKey.from_public_bytes(peer_pub_key)) #Общий секрет соответвенно у пира получается то же самое
    except:
        print(peer_pub_key, peer_salt)
    derive_key = hkdf_expand_label(cl_shared_key,b'derived',b'',48) #Тут тоже
    #Hello Hash
    hello_hash = hashlib.sha256()
    hellot = (peer_salt + cl_salt
    + cl_pub_key.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
    + peer_pub_key)
    hello_hash.update(hellot) #Использовал другую библиотеку для хэша , но тоже на OpenSSl ,поскольку в cryptography я не нашёл способа
    #сериализовать хэш 😒😒
    hello_hash = hello_hash.digest()
    #HandShake secret и тд
    hand_key = hkdf_extract(derive_key, cl_shared_key) #вот это я "списал" с сайта ,правда там было написано на rust(в целом почти ничего не поменялось) с библиотекой Openssl(поскольку cryptography это openssl для питон ,всё должно работать)
    cl_temp_key = hkdf_expand_label(hand_key,b'c hs temp',hello_hash,48)
    peer_temp_key = hkdf_expand_label(hand_key,b'p hs temp',hello_hash,48)
    cl_hand_key = hkdf_expand_label(cl_temp_key,b'key',b'',ckl)
    peer_hand_key = hkdf_expand_label(peer_temp_key,b'key',b'',ckl)
    cl_hand_iv = hkdf_expand_label(cl_temp_key,b'iv',b'',cil)
    peer_hand_iv = hkdf_expand_label(peer_temp_key ,b'iv',b'',cil)
    seq_num = 0
    main(cl_hand_key,cl_hand_iv,peer_hand_key,peer_hand_iv)
    return cl_hand_key , cl_hand_iv , peer_hand_key , peer_hand_iv , hand_key , hello_hash

#Правда я пропустил важный(насколько там было написано) шаг. с помощью сгенерированных ранее ключей и iv собеседники должны договорится и сгнерировать
#абсолютно новые пары iv и key для полной безопастности ,но мне показалось то что тут я могу почему это пропустить(уже не помню почему)

def get_nonce(seqnum,iv): #получение nonce
    tseq = seqnum.to_bytes(cil,'big')
    nonce = bytes(x ^ y for x, y in zip(tseq,iv))
    return nonce

def crypt(mess,key,iv): #Зашифровка
    global seq_num
    aes = AESGCM(key)
    seq_num += 1
    nonce = get_nonce(seq_num,iv)
    #Создание AAD
    aad = (bytes.fromhex('170303') +
    (len(mess)).to_bytes(2, 'big')) #Тип(17), протокол(0303)(не знаю, нужно ли это), длина + 16
    #Шифрование
    cl_crypt_mess = aes.encrypt(
        nonce,
        str(mess).encode(),
        aad
    )
    cl_crypt_rec = ('б' + str(str(seq_num).encode() + cl_crypt_mess + aad) + 'б') #Возможно ,помещать seqnum и aad в сообщение нельзя ,если это так ,то напишите
    wtext(cl_crypt_rec,Pid)# пишет текст в приложение , буквы б для get_data()
    print(nonce,aad,cl_crypt_rec) # это строка для перепроверки
    return cl_crypt_rec, cl_crypt_mess

def decrypt(n,key,iv,mss = 0): #Дешифровка
    global seq_num
    #Восстановление AAD
    if mss == 0:
        hmess = get_data(2,readt(findPid(), n)[1])
    else:
        hmess = get_data(2,mss)
    for mes in hmess:
        x = len(mes)
        aad = mes[x - 5:x]
        #Восстановление сообщения
        mess = mes[1:len(mes)-5]
        #деШифрование
        seq_num = int(str(mes)[2])
        nonce = get_nonce(seq_num,iv)
        aes = AESGCM(key)
        uncrypt_mess = aes.decrypt(
            nonce,
            mess,
            aad
        )
        norm_mess = urllib.parse.unquote(uncrypt_mess)
    return norm_mess, uncrypt_mess

dtext('Перед тем как начать ,перейдите в чат с вашим собеседником\n(Убедитесь ,что у вашего собеседника тоже установлен SEC), а затем нажмите Готово',150,20,txt2='Готово',func = handshake)
'''
f = str(input()) #"ручное" управление фунциями
while f != 0:
    print(eval(f))
    f = str(input()) 
'''
#в коде есть баг: либо в wtext либо в get_data иногда теряются байты ключа и соли. почему я не знаю. происходит где-то раз в 30 случаев(надеюсь запускать это 30 раз вы не будете)
