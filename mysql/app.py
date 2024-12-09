from flask import Flask, request, render_template
import mysql.connector

app = Flask(__name__)

# Configuración de conexión a la base de datos
DB_CONFIG = {
    'host': 'localhost',       # Cambiar por el host de tu base de datos
    'user': 'cajero',      # Usuario de MySQL
    'password': '1234',  # Contraseña de MySQL
    'database': 'db_bank'      # Nombre de la base de datos
}

def get_db_connection():
    """Establece la conexión a la base de datos."""
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/get_card', methods=['GET'])
def get_card():
    """Endpoint para obtener y desencriptar tarjetas."""
    customer_id = request.args.get('customer')  # Obtener el parámetro de la URL
    
    if not customer_id:
        return "El parámetro 'customer' es obligatorio.", 400

    try:
        # Conexión a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Consulta para desencriptar las tarjetas
        query = """
            SELECT 
                c.creditCard AS creditCard,
                AES_DECRYPT(c.encryptedCC, 'my_secret_key') AS decryptedCC
            FROM cards c
            WHERE c.customer_id = %s;
        """
        cursor.execute(query, (customer_id,))
        
        # Obtener resultados
        rows = cursor.fetchall()
        cards = [{"creditCard": row["creditCard"], "decryptedCC": row["decryptedCC"].decode()} for row in rows]

        cursor.close()
        conn.close()

        # Si no hay resultados
        if not cards:
            return render_template('cards.html', customer_id=customer_id, cards=None)

        # Renderizar resultados en HTML
        return render_template('cards.html', customer_id=customer_id, cards=cards)

    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)