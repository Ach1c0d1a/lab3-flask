from flask import Flask, render_template, jsonify, request
from sqlalchemy import create_engine, text
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

app = Flask(__name__)

# Configuración de la conexión a la base de datos
DB_URI = "mssql+pyodbc://cajero:1234@127.0.0.1/db_bank?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(DB_URI)

# Clave de desencriptación (debe coincidir con la usada en SQL Server)
SYMMETRIC_KEY = b'lscck_04'[:64]

def decrypt_aes256(encrypted_data):
    """Desencripta un dato cifrado con AES-256"""
    try:
        cipher = AES.new(SYMMETRIC_KEY, AES.MODE_ECB)  # Modo ECB usado como ejemplo
        decrypted_data = unpad(cipher.decrypt(base64.b64decode(encrypted_data)), AES.block_size)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"Error en desencriptación: {e}")
        return None

@app.route('/get_card/<customer_id>', methods=['GET'])
def get_card(customer_id):
    """Endpoint para obtener y desencriptar tarjetas de un cliente"""
    with engine.connect() as conn:
        # Recupera los datos cifrados
        result = conn.execute(text("""
            OPEN SYMMETRIC KEY lscck_04 DECRYPTION BY CERTIFICATE secure_credit_cards;
            SELECT creditCard, CONVERT(VARCHAR, DecryptByKey(encryptedCC)) as decryptedCC
            FROM cards WHERE customer = :customer_id;
            CLOSE SYMMETRIC KEY lscck_04;
        """), {"customer_id": customer_id})
        cards = [{"creditCard": row["creditCard"], "decryptedCC": row["decryptedCC"]} for row in result]

    return jsonify(cards)

@app.route('/html_cards/<customer_id>')
def html_cards(customer_id):
    """Muestra las tarjetas en un archivo HTML"""
    response = get_card(customer_id)
    cards = response.json
    return render_template('cards.html', cards=cards)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
