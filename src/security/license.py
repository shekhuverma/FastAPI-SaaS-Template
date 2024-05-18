from base64 import b64decode, b64encode

from Crypto.Cipher import AES

from src.settings import LicenseGenSettings


class LicenseGen:
    def __init__(self):
        self.IV = LicenseGenSettings.INITIALISATION_VECTOR.encode("utf8")
        self.str_key = LicenseGenSettings.SECRET_KEY
        self.aes_obj = AES.new(self.str_key.encode("utf-8"), AES.MODE_CFB, self.IV)

    def create(self, str_to_enc):
        hx_enc = self.aes_obj.encrypt(str_to_enc.encode("utf8"))
        mret = b64encode(hx_enc).decode("utf-8")
        return mret

    def decrypt(self, enc_str):
        str_tmp = b64decode(enc_str.encode("utf-8"))
        str_dec = self.aes_obj.decrypt(str_tmp)
        mret = str_dec.decode("utf-8")
        return mret
