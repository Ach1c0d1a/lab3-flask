from flask import Flask, request, jsonify
import pyodbc
import rsa

app = Flask(__name__)

# Configuración de la conexión a la base de datos
DB_CONFIG = {
    'server': 'localhost',
    'database': 'db_bank',
    'username': 'cajero',
    'password': 1234
}

def get_db_connection():
    """Conecta a la base de datos y retorna la conexión"""
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']}"
    )
    return conn

(public_key, private_key) = rsa.newkeys(512)

@app.route('/get-customer-card', methods=['GET'])
def get_customer_card():
    customer_id = request.args.get('customer_id')
    
    if not customer_id:
        return jsonify({"error": "Falta el parámetro 'customer_id'"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Consulta SQL
        query = (
            "select cd.creditCard from customer c"
            "inner join cards cd"
            "on cd.customer = c.cedcustomer"
            "where cd.customer = ?;"
        )
        cursor.execute(query, customer_id)
        rows = cursor.fetchall()
        
        # Si no se encuentran datos
        if not rows:
            return jsonify({"error": "No se encontraron tarjetas para este cliente"}), 404
        
        # Procesar los resultados y convertir el mensaje cifrado
        result = [
            {
                "creditCard": row[0],
                "encryptedCC": row[1].hex() if isinstance(row[1], bytes) else row[1],  # Convierte los bytes a hexadecimal si es necesario
                "decryptedCC": row[2]
            }
            for row in rows
        ]
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
