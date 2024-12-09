-- Crear la base de datos
CREATE DATABASE db_bank;
USE db_bank;

-- Crear la tabla de clientes
CREATE TABLE customer (
    cedcustomer VARCHAR(20) NOT NULL,
    nombre VARCHAR(30),
    correo VARCHAR(30),
    PRIMARY KEY (cedcustomer)
);

-- Crear la tabla de tarjetas
CREATE TABLE cards (
    customer VARCHAR(20) NOT NULL,
    creditCard VARCHAR(25) NOT NULL,
    encryptedCC VARBINARY(250),
    PRIMARY KEY (creditCard),
    FOREIGN KEY (customer) REFERENCES customer(cedcustomer)
);

-- Insertar datos en la tabla de clientes
INSERT INTO customer (cedcustomer, nombre, correo)
VALUES ('605960578', 'Juanito', 'juani17@gmail.com');

-- Insertar datos en la tabla de tarjetas
-- En MySQL utilizamos AES_ENCRYPT para cifrar los datos
INSERT INTO cards (customer, creditCard, encryptedCC)
VALUES (
    '605960578',
    '6042210012564010',
    AES_ENCRYPT('6042210012564010', 'my_secret_key')
);

-- Consultar datos desencriptados
-- Utilizamos AES_DECRYPT para desencriptar
SELECT 
    cd.creditCard,
    AES_DECRYPT(cd.encryptedCC, 'my_secret_key') AS decryptedCard
FROM cards cd
INNER JOIN customer c ON cd.customer = c.cedcustomer
WHERE cd.customer = '605960578';
