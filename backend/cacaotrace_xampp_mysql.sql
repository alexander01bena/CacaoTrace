-- ============================================================
-- BASE DE DATOS CacaoTrace para XAMPP / MySQL / MariaDB
-- Proyecto: CacaoTrace Python mejorado
-- Uso: phpMyAdmin > SQL > pegar/ejecutar este script
-- ============================================================

CREATE DATABASE IF NOT EXISTS cacaotrace
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE cacaotrace;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS movimientos_inventario;
DROP TABLE IF EXISTS poscosecha;
DROP TABLE IF EXISTS controles_calidad;
DROP TABLE IF EXISTS lotes;
DROP TABLE IF EXISTS recepciones;
DROP TABLE IF EXISTS fincas;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS productores;
DROP TABLE IF EXISTS roles;

SET FOREIGN_KEY_CHECKS = 1;

-- =========================
-- TABLA: roles
-- =========================
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(150) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- TABLA: productores
-- =========================
CREATE TABLE productores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(120) NOT NULL,
    documento VARCHAR(30) NULL UNIQUE,
    telefono VARCHAR(30) NULL,
    direccion VARCHAR(150) NULL,
    municipio VARCHAR(80) DEFAULT 'San Andrés de Tumaco',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- TABLA: users
-- =========================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active_user TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    role_id INT NOT NULL,
    CONSTRAINT fk_users_roles
        FOREIGN KEY (role_id) REFERENCES roles(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- TABLA: fincas
-- =========================
CREATE TABLE fincas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    vereda VARCHAR(120) NULL,
    municipio VARCHAR(80) DEFAULT 'San Andrés de Tumaco',
    hectareas DOUBLE NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    productor_id INT NOT NULL,
    CONSTRAINT fk_fincas_productores
        FOREIGN KEY (productor_id) REFERENCES productores(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- TABLA: recepciones
-- =========================
CREATE TABLE recepciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_cacao VARCHAR(30) NOT NULL,
    cantidad_kg DOUBLE NOT NULL,
    fecha_recepcion DATE NOT NULL,
    observaciones TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    productor_id INT NOT NULL,
    finca_id INT NOT NULL,
    CONSTRAINT fk_recepciones_productores
        FOREIGN KEY (productor_id) REFERENCES productores(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_recepciones_fincas
        FOREIGN KEY (finca_id) REFERENCES fincas(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- TABLA: lotes
-- =========================
CREATE TABLE lotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    cantidad_inicial_kg DOUBLE NOT NULL,
    cantidad_actual_kg DOUBLE NOT NULL,
    estado VARCHAR(40) DEFAULT 'Recepción',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    productor_id INT NOT NULL,
    finca_id INT NOT NULL,
    recepcion_id INT NOT NULL,
    CONSTRAINT fk_lotes_productores
        FOREIGN KEY (productor_id) REFERENCES productores(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_lotes_fincas
        FOREIGN KEY (finca_id) REFERENCES fincas(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_lotes_recepciones
        FOREIGN KEY (recepcion_id) REFERENCES recepciones(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- TABLA: controles_calidad
-- =========================
CREATE TABLE controles_calidad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    humedad DOUBLE NOT NULL,
    estado_grano VARCHAR(60) NOT NULL,
    clasificacion VARCHAR(60) NOT NULL,
    observaciones TEXT NULL,
    fecha_control DATETIME DEFAULT CURRENT_TIMESTAMP,
    lote_id INT NOT NULL,
    CONSTRAINT fk_controles_lotes
        FOREIGN KEY (lote_id) REFERENCES lotes(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- TABLA: poscosecha
-- =========================
CREATE TABLE poscosecha (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fermentacion VARCHAR(80) NOT NULL,
    secado VARCHAR(80) NOT NULL,
    estado_proceso VARCHAR(80) NOT NULL,
    observaciones TEXT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    lote_id INT NOT NULL,
    CONSTRAINT fk_poscosecha_lotes
        FOREIGN KEY (lote_id) REFERENCES lotes(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- TABLA: movimientos_inventario
-- =========================
CREATE TABLE movimientos_inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(30) NOT NULL,
    cantidad_kg DOUBLE NOT NULL,
    motivo VARCHAR(160) NULL,
    fecha_movimiento DATETIME DEFAULT CURRENT_TIMESTAMP,
    lote_id INT NOT NULL,
    CONSTRAINT fk_movimientos_lotes
        FOREIGN KEY (lote_id) REFERENCES lotes(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- DATOS ACTUALES MIGRADOS DESDE cacaotrace.db
-- ============================================================

-- Datos de roles
INSERT INTO roles (id, name, description) VALUES (1, 'administrador', 'Gestiona usuarios, productores, fincas y reportes.');
INSERT INTO roles (id, name, description) VALUES (2, 'recepcion', 'Registra entradas de cacao y creación de lotes.');
INSERT INTO roles (id, name, description) VALUES (3, 'calidad', 'Registra controles de calidad y poscosecha.');

-- Datos de productores
INSERT INTO productores (id, nombres, documento, telefono, direccion, municipio, created_at) VALUES (1, 'Alex', '12345', '322563373', 'avenida la playa', 'San Andrés de Tumaco', '2026-05-05 17:12:03.911248');

-- Datos de users
INSERT INTO users (id, username, email, password_hash, is_active_user, created_at, role_id) VALUES (1, 'admin', 'admin@cacaotrace.local', 'scrypt:32768:8:1$UrndBlImIrYdYw8t$5fdf40d1d474241e7be55d302fbae5543b6925420b849426baf93128b14fc2bcc01a87b83b2479988e783b063133bf7b23a1635bcafcc26b8fa2dd173f0b927b', 1, '2026-05-03 02:53:16.804706', 1);
INSERT INTO users (id, username, email, password_hash, is_active_user, created_at, role_id) VALUES (2, 'Angel', 'gabohurtado29@gmail.com', 'scrypt:32768:8:1$H6KMWaBiW80EKyqj$ec16461ed14c767d16206503914caef76a5c4d9900f50cff7c59ee785b1c79653c91876b6957872cdaadc052a5b385b7dd1b1a82b36f1ab5fc5228673aad4e75', 1, '2026-05-03 02:54:57.882092', 2);
INSERT INTO users (id, username, email, password_hash, is_active_user, created_at, role_id) VALUES (3, 'Miguel', 'aaaaaaa@gmail.com', 'scrypt:32768:8:1$ZrDDzY0WBl8HugWn$390a6ca9748b651e4f612735a3b4ebb125011f0d4b8227e19cfcdbadf8067866c2601ab5899f5d0f1d411d75ea20974a32fc4576a3dd484b9be78f1b18eedde7', 1, '2026-05-03 02:58:28.050830', 3);

-- Datos de fincas
INSERT INTO fincas (id, nombre, vereda, municipio, hectareas, created_at, productor_id) VALUES (1, 'La victoria', 'bucheli', 'San Andrés de Tumaco', 2.0, '2026-05-05 17:13:08.039089', 1);

-- Datos de recepciones
INSERT INTO recepciones (id, tipo_cacao, cantidad_kg, fecha_recepcion, observaciones, created_at, productor_id, finca_id) VALUES (1, 'Cacao fresco', 50.0, '2026-05-05', 'Bolsa cafe rotulada como 1k', '2026-05-05 17:14:09.480599', 1, 1);

-- Datos de lotes
INSERT INTO lotes (id, codigo, cantidad_inicial_kg, cantidad_actual_kg, estado, fecha_creacion, productor_id, finca_id, recepcion_id) VALUES (1, 'LOT-2026-0001', 50.0, 70.0, 'Inventario', '2026-05-05 17:14:09.492939', 1, 1, 1);

-- Datos de controles_calidad
INSERT INTO controles_calidad (id, humedad, estado_grano, clasificacion, observaciones, fecha_control, lote_id) VALUES (1, 20.0, 'Regular', 'Calidad media', '', '2026-05-05 17:14:31.158294', 1);

-- Datos de poscosecha
INSERT INTO poscosecha (id, fermentacion, secado, estado_proceso, observaciones, fecha_registro, lote_id) VALUES (1, 'En proceso', 'En proceso', 'Fermentación', '', '2026-05-05 17:14:58.428225', 1);

-- Datos de movimientos_inventario
INSERT INTO movimientos_inventario (id, tipo, cantidad_kg, motivo, fecha_movimiento, lote_id) VALUES (1, 'Entrada', 50.0, 'Recepción inicial del lote', '2026-05-05 17:14:09.495183', 1);
INSERT INTO movimientos_inventario (id, tipo, cantidad_kg, motivo, fecha_movimiento, lote_id) VALUES (2, 'Entrada', 20.0, 'Agregar prroducto', '2026-05-05 17:16:31.721496', 1);

-- Ajuste de AUTO_INCREMENT para continuar después de los datos importados
ALTER TABLE roles AUTO_INCREMENT = 4;
ALTER TABLE productores AUTO_INCREMENT = 2;
ALTER TABLE users AUTO_INCREMENT = 4;
ALTER TABLE fincas AUTO_INCREMENT = 2;
ALTER TABLE recepciones AUTO_INCREMENT = 2;
ALTER TABLE lotes AUTO_INCREMENT = 2;
ALTER TABLE controles_calidad AUTO_INCREMENT = 2;
ALTER TABLE poscosecha AUTO_INCREMENT = 2;
ALTER TABLE movimientos_inventario AUTO_INCREMENT = 3;

-- Usuario inicial incluido:
-- usuario: admin
-- contraseña original del proyecto: admin123
