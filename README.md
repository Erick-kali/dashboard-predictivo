1. descomprime la carpeta
2. instalar los requirimientos  pip install -r requirements.txt
3. crear la base de datos
   create database sin_sentido;
use sin_sentido;
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);
select*from usuarios;
CREATE TABLE personas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    edad INT,
    genero VARCHAR(1), -- M o F
    ingreso DECIMAL(10,2)
);

INSERT INTO personas (edad, genero, ingreso) VALUES (25, 'M', 1500.00);
INSERT INTO personas (edad, genero, ingreso) VALUES (30, 'F', 2000.00);
INSERT INTO personas (edad, genero, ingreso) VALUES
(22, 'M', 1200.00),
(28, 'F', 2100.00),
(35, 'M', 3100.00),
(40, 'F', 2700.00),
(23, 'M', 1500.00),
(31, 'F', 2300.00),
(29, 'M', 2900.00),
(26, 'F', 1800.00),
(33, 'M', 3200.00),
(27, 'F', 1950.00),
(24, 'M', 1300.00),
(38, 'F', 2800.00),
(30, 'M', 2500.00),
(36, 'F', 2900.00),
(25, 'M', 1600.00),
(32, 'F', 2400.00),
(34, 'M', 3000.00),
(29, 'F', 2100.00),
(28, 'M', 2700.00),
(35, 'F', 2600.00),
(23, 'M', 1400.00),
(30, 'F', 2200.00),
(37, 'M', 3300.00),
(41, 'F', 3100.00),
(26, 'M', 1800.00),
(33, 'F', 2700.00),
(31, 'M', 2900.00),
(27, 'F', 2000.00),
(29, 'M', 2500.00),
(34, 'F', 2800.00),
(22, 'M', 1250.00),
(39, 'F', 3000.00),
(35, 'M', 3200.00),
(40, 'F', 2900.00),
(24, 'M', 1350.00),
(31, 'F', 2300.00),
(30, 'M', 2600.00),
(28, 'F', 2200.00),
(33, 'M', 3100.00),
(27, 'F', 2100.00),
(25, 'M', 1700.00),
(36, 'F', 2950.00),
(29, 'M', 2750.00),
(38, 'F', 2850.00),
(26, 'M', 1900.00),
(32, 'F', 2450.00),
(30, 'M', 2650.00),
(28, 'F', 2150.00),
(34, 'M', 3050.00),
(27, 'F', 2250.00);
4. iniciar main.py
grupo 4c
Erick Arce
Maritza Munoz
Gabriel 
Narcisa Camacho