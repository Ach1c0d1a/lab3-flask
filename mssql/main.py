from flask import Flask, request, jsonify
import pyodbc
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA1
import base64

app = Flask(__name__)

# Configuración de la conexión a la base de datos
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=db_bank;'
        'UID=cajero;'
        'PWD=1234'
    )
    return conn

# Función para descifrar los datos utilizando AES
def decrypt_data(encrypted_data, key):
    # Decodificar desde Base64
    encrypted_data_bytes = base64.b64decode(encrypted_data)
    
    # El IV (primeros 16 bytes) y el texto cifrado (resto)
    iv = encrypted_data_bytes[:16]
    encrypted_text = encrypted_data_bytes[16:]
    
    # Crear el objeto AES
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Descifrar y eliminar el padding
    decrypted = unpad(cipher.decrypt(encrypted_text), AES.block_size)
    
    return decrypted.decode('utf-8')

@app.route('/get-customer-card', methods=['GET'])
def get_customer_card():
    customer_id = request.args.get('customer_id')

    if not customer_id:
        return jsonify({"error": "Falta el parámetro 'customer_id'"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ejecutar la consulta para obtener el número de tarjeta cifrado
        cursor.execute(
            "select cd.creditCard"
            "CONVERT(varchar, DecryptByKey(cd.encryptedCC,1,HashBytes('SHA1',convert(varbinary,500)))) decryptedCC"
            "from customer c inner join cards cd"
            "on cd.customer = c.cedcustomer"
            "where cd.customer = ?;"
        , customer_id)

        row = cursor.fetchone()

        if row:
            encrypted_cc = row.encryptedCC
            # Usar la misma clave y IV con el que se cifró la tarjeta
            # Este ejemplo asume que la clave AES se almacena o genera en otro lugar.
            # Aquí, usaremos una clave estática solo para este ejemplo.
            aes_key = b'lscck_04'  # Clave AES-256 de 32 bytes
            decrypted_cc = decrypt_data(encrypted_cc, aes_key)
            
            return jsonify({
                "customer_id": customer_id,
                "credit_card": row.creditCard,
                "decrypted_credit_card": decrypted_cc
            })
        else:
            return jsonify({"error": "No se encontró el cliente"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
