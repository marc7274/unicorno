import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from json import load
from time import asctime,sleep
from socket import gethostname
from os import remove
from cv2 import VideoCapture,imwrite
from hash_manager import get_hash,restore_hash

#metodo che compone la mail
def mail_header(From,To,CC,Subject,Text):
    msg = MIMEMultipart()
    msg['From'] = From
    msg['To'] = To
    msg['CC'] = ','.join(CC)
    msg['Subject'] = Subject
    msg.attach(MIMEText(Text,'plain'))
    return msg

#metodo che permette di allegare un file alla mail
def attach_file(filename,delete:bool):
    with open(filename, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename= {filename}',
    )
    if delete:
        remove(filename)
    return part

#metodo per la cattura della immagine dalla webcam
def capture(filename):
    cam = VideoCapture(0)
    result, image = cam.read()
    if result:
        imwrite(filename, image)

if __name__ == '__main__':
    #import delle impostazioni dai file di configurazione
    credentials = load(open('credentials.json','r'))
    config = load(open('config.json','r'))
    #import dell'hash della password corretta da file preesistente
    old_hash = ""
    with open(config['user']+'_hash') as old_hash_file:
        old_hash = old_hash_file.readline()
    
    while True:
        sleep(config['sleep_time'])
        #controllo se l'hash corrente dell'utente specificato è uguale a quello salvato nel file
        if get_hash(config['user']) != old_hash:
            #ripristino del vecchio hash e quindi della vecchia password
            restore_hash(config['user'])
            #creazione della mail
            text = '{}\nE\' stata cambiata la password sul pc {}.'.format(asctime(),gethostname())
            msg = mail_header(config['From'],config['To'],config['CC'],config['Subject'],text)
            #cattura della immagine
            capture('image.png')
            #l'immagine viene allegata alla mail
            msg.attach(attach_file(config['image_name'],config['image_delete']))
            
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(config['smtp'], config['port'], context=context) as server:
                #login per l'invio della mail
                server.login(credentials['email'], credentials['passwd'])
                #invio della mail
                server.sendmail(config['From'], config['CC'] + [config['To']], msg.as_string())  