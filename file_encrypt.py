from cryptography.fernet import Fernet
import os
import pathlib


file = open('key.key', 'rb')
key = file.read()
file.close()

with open('chat.jpg', 'rb') as f:
    data = f.read()

fernet = Fernet(key)
encrypted = fernet.encrypt(data)

with open('file.encrypted', 'wb') as f:
    f.write(encrypted)
