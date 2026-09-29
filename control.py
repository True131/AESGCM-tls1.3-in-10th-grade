from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pyexpat.errors import messages
from pywinauto import Desktop
import pywinauto
import pyautogui
import psutil
import pyclip
import codecs
import time

pourcent = 125
meslen = round(35 * (pourcent/100))

def findPid(name = "Telegram.exe"): #поиск PId мессенджера ,код я делал для телеграмм потому что не хочу скачивать max , но там он тоже должен работать , но только надо добавить полный ручной ввод и отправку ключей и др
    for x in psutil.process_iter(['pid', 'name']):
        if x.info['name'] == name:
            Pid = x.info['pid']
    return Pid

def wtext(mess,Pid): #отправка текста в мессенджер
    app = Application(backend='uia').connect(process=Pid)
    #print(app.Dialog.print_control_identifiers())
    dlg = app.window(best_match ='Dialog')
    #print(dlg.print_control_identifiers())
    edit = dlg.child_window(control_type="Edit",found_index=1)
    edit.click_input()
    dlg.set_focus()
    edit.set_text(f'{mess}')
    edit.type_keys('{ENTER}')

def readt(Pid,n): #чтение сообщения с помощью их выделения и копирования
    app = Application(backend='uia').connect(process=Pid)
    #print(app.Dialog.print_control_identifiers())
    dlg = app.window(best_match ='Dialog')
    edit = dlg.child_window(control_type="Edit",found_index=1)
    edit.click_input()
    dlg.set_focus()
    mousex ,mousey = pyautogui.position()
    mousey = mousey - round(40 * (pourcent/100))
    if n > 0: #Это чтобы выделять n сообщений
        pywinauto.mouse.press(button='left',coords=(mousex,mousey))
        mousey = mousey - round(meslen * n)
        pywinauto.mouse.release(button='left', coords=(mousex , mousey))
        send_keys('{VK_CONTROL down}' 'c' '{VK_CONTROL up}')
        time.sleep(1.5)
    if n == 0: #Чтобы выделять 1 сообщения ,но я забыл используется ли это вообще
        mousey = mousey - round(meslen * 0.5)
        pywinauto.mouse.click(button='right', coords=(mousex , mousey))
        mousex = mousex + round(10 * (pourcent/100))
        mousey = mousey - round(10 * (pourcent/100))
        pywinauto.mouse.click(button='left', coords=(mousex , mousey))
        pywinauto.mouse.click(button='right', coords=(mousex , mousey))
        mousex = mousex + round(10 * (pourcent/100))
        mousey = mousey + round(10 * (pourcent/100))
        pywinauto.mouse.click(button='left', coords=(mousex, mousey))
        send_keys('^c')
        time.sleep(0.5)
    edit = dlg.child_window(title="Отмена")
    edit.click_input()
    return codecs.decode(pyclip.paste(),'unicode_escape').encode('latin1') ,pyclip.paste().decode(), pyclip.clear()