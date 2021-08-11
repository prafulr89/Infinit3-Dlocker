from cryptography.fernet import Fernet
from Crypto.Cipher import AES
from secrets import token_bytes

key = Fernet.generate_key()
print(key)

file = open('key.key', 'wb')
file.write(key)
file.close()