import binascii

class NeoCript:

    def decrypt(string):
        try:
            # Decriptografa
            binstr = binascii.a2b_base64(string)
            hexBased = binascii.hexlify(binstr)
            hexBased = (bytes(hexBased[len(hexBased) - 1 :]) + bytes(hexBased[:-1]))[2:]
            result = binascii.unhexlify(hexBased).decode("utf-8").replace("\n", "")

            # Retorna o valor
            return result
        except:
            # Retorna o valor vazio
            return ""
        
    def encrypt(string):
        try:
            # Criptografa
            hexBased = "6" + (string).encode("utf-8").hex() + "1"
            binstr = binascii.unhexlify(hexBased)
            result = binascii.b2a_base64(binstr)

            # Retorna o valor
            return result
        except:
            # Retorna o valor vazio
            return ""

    def decrypt_values(dict):

        # Inicializa o dict
        decrypt_dict = {}
     
        # Percorre as chaves
        for key in dict:
        
            # Decriptografa
            try:
                binstr      = binascii.a2b_base64(dict[key])
                hexBased    = binascii.hexlify(binstr)
                hexBased    = (bytes(hexBased[len(hexBased) - 1 :]) + bytes(hexBased[:-1]))[2:]
                result      = binascii.unhexlify(hexBased).decode("utf-8").replace("\n", "")
            except:
                # Retorna a mesma string
                result = dict[key]
            
            # Adiciona o valor no novo dict
            decrypt_dict[key] = result
        
        # Retorna o dict
        return decrypt_dict.values()
    
    def encrypt_values(dict):

        # Inicializa o dict
        encrypt_dict = {}
     
        # Percorre as chaves
        for key in dict:
        
            # Criptografa
            try:
                hexBased = "6" + (dict[key]).encode("utf-8").hex() + "1"
                binstr = binascii.unhexlify(hexBased)
                result = binascii.b2a_base64(binstr)
            except:
                # Retorna a mesma string
                result = dict[key]
            
            # Adiciona o valor no novo dict
            encrypt_dict[key] = result
        
        # Retorna o dict
        return encrypt_dict.values()
