from werkzeug.security import check_password_hash
import hashlib


if __name__=="__main__":
    password=input('Texto a encriptar: ')
    result = hashlib.md5(bytes(password, encoding='utf-8'))
    print('{}'.format(result.hexdigest()))
    input('')
