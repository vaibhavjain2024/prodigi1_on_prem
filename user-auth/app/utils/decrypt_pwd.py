from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
from app.config.config import AES256_ENCRYPT_KEY as KEY

# KEY = 'm6Cl+NAZ2hqxx8Ulg0WlXR16oiY1zG3O/OyJLKfmbFk='

class AES256:
    def decrypt(self, encrypted):
        # Decode the Base64 encoded key and encrypted message
        decoded_key = base64.b64decode(KEY)
        decoded_encrypted = base64.b64decode(encrypted)

        # Create a new AES cipher object
        cipher = AES.new(decoded_key, AES.MODE_ECB)

        # Decrypt the message
        decrypted = cipher.decrypt(decoded_encrypted)

        # Unpad the decrypted message to remove padding
        unpadded_decrypted = unpad(decrypted, AES.block_size)

        return unpadded_decrypted.decode('utf-8')


if __name__ == '__main__':
    # Create an instance of the AES256 class
    aes = AES256()
    encrypted_text = 'UYra1qWtnxnmRPciPk/twg=='
    # Decrypt the messages
    decrypted_message_1 = aes.decrypt(encrypted_text)
    # Print the decrypted messages
    print("Decrypted Message :", decrypted_message_1)

