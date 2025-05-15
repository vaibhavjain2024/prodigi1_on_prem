import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;

public class Aes256 {

    // Method to encrypt a given text using AES-256
    public static String encrypt(String text, String base64Key) throws Exception {
        // Decode the Base64 encoded key
        byte[] decodedKey = Base64.getDecoder().decode(base64Key);
        
        // Create a secret key from the decoded key bytes
        SecretKey secretKey = new SecretKeySpec(decodedKey, 0, decodedKey.length, "AES");
        
        // Initialize the cipher for encryption
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding"); // Using ECB mode with PKCS5 padding
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        
        // Encrypt the text
        byte[] encryptedBytes = cipher.doFinal(text.getBytes());
        
        // Return the encrypted text in Base64 format
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }

    public static void main(String[] args) {
        try {
            String textToEncrypt = "password"; // The text to be encrypted
            String base64Key = "m6Cl+NAZ2hqxx8Ulg0WlXR16oiY1zG3O/OyJLKfmbFk="; // Your Base64 encoded key
            
            // Encrypt the text
            String encrypted = encrypt(textToEncrypt, base64Key);
            System.out.println("Encrypted Text: " + encrypted);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
