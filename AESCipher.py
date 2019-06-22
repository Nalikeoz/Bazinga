from Crypto.Cipher import AES
from hashlib import md5

ENC_KEY = md5('ma kore huri?').hexdigest()
PADDING_CHAR = '*'
IMAGE_SUFFIX = 'IMG'
START_OF_ENC = 'START'


class AESCipher(object):
    def __init__(self):
        self.encryption_suite = AES.new(ENC_KEY)

    def encrypt(self, text_to_enc):
        """
        @param text_to_enc: the message that will be encrypted(string).
        @return: the function gets a string and return his AES encryption.
        """
        enc_message = text_to_enc + PADDING_CHAR * (16 - len(text_to_enc) % 16)
        enc_message = self.encryption_suite.encrypt(enc_message)
        return enc_message

    def decrypt(self, enc_text):
        """
        @param enc_text: an AES encrypted message.
        @return: the function gets an encrypted message and returns his decrypted string.
        """
        dec_message = self.encryption_suite.decrypt(enc_text)
        dec_message = dec_message.rstrip(PADDING_CHAR)
        return dec_message

    def encrypt_image(self, image_data):
        last_16_bytes = image_data[-16:]
        enc_image = self.encrypt(last_16_bytes)
        enc_image = image_data[:-16] + START_OF_ENC + enc_image + IMAGE_SUFFIX
        return enc_image

    def decrypt_image(self, enc_image_data):
        encrypted_bytes = enc_image_data[enc_image_data.find(START_OF_ENC) + len(START_OF_ENC):]
        dec_last_16 = self.decrypt(encrypted_bytes)
        enc_image_data = enc_image_data[:enc_image_data.find(START_OF_ENC)] + dec_last_16
        return enc_image_data
