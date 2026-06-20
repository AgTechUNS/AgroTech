-- AgroTech - Esquema de Base de Datos Relacional
-- Basado en: src/infrastructure/relational_repo/models.py
-- Motor: PostgreSQL (compatible Neon)

-- ============================================================
-- ENTIDADES INDEPENDIENTES
-- ============================================================

CREATE TABLE IF NOT EXISTS usuario (
    email_usuario  VARCHAR(255) PRIMARY KEY,
    nombre         VARCHAR(255) NOT NULL,
    telefono       VARCHAR(50),
    hash_password  VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS campo (
    nombre_campo      VARCHAR(255) PRIMARY KEY,
    coordenadas_campo TEXT NOT NULL,        -- Polígono GeoJSON
    descripcion_campo TEXT
);

CREATE TABLE IF NOT EXISTS rol (
    nombre_rol  VARCHAR(100) PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS cultivo (
    nombre_cultivo VARCHAR(255) PRIMARY KEY,
    variedad       VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS sensor (
    nombre_codigo_sensor VARCHAR(255) PRIMARY KEY,
    estado               BOOLEAN NOT NULL DEFAULT TRUE  -- TRUE=activo, FALSE=inactivo
);

CREATE TABLE IF NOT EXISTS imagen_satelital (
    id_imagen      VARCHAR(255) PRIMARY KEY,
    fecha_captura  TIMESTAMPTZ NOT NULL,
    proveedor      VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS ejecucion_batch (
    fecha_ini  TIMESTAMPTZ PRIMARY KEY,
    estado     VARCHAR(50) NOT NULL,  -- EN_CURSO, COMPLETADO, FALLIDO
    fecha_fin  TIMESTAMPTZ
);

-- ============================================================
-- ENTIDADES DEPENDIENTES (Jerárquicas)
-- ============================================================

CREATE TABLE IF NOT EXISTS parcela (
    nombre_parcela      VARCHAR(255) PRIMARY KEY,
    coordenadas_parcela TEXT NOT NULL,          -- Polígono GeoJSON
    descripcion_parcela TEXT,
    nombre_campo        VARCHAR(255) NOT NULL,
    FOREIGN KEY (nombre_campo) REFERENCES campo(nombre_campo)
);

CREATE TABLE IF NOT EXISTS regla (
    nombre_regla      VARCHAR(255) NOT NULL,
    nombre_campo      VARCHAR(255) NOT NULL,
    formula           TEXT NOT NULL,            -- Expresión de la regla agroclimática
    descripcion_regla TEXT,
    umbral            FLOAT NOT NULL,
    PRIMARY KEY (nombre_regla, nombre_campo),
    FOREIGN KEY (nombre_campo) REFERENCES campo(nombre_campo)
);

CREATE TABLE IF NOT EXISTS ventana_temporal (
    fecha_ini      TIMESTAMPTZ NOT NULL,
    fecha_fin      TIMESTAMPTZ NOT NULL,
    nombre_parcela VARCHAR(255) NOT NULL,
    PRIMARY KEY (fecha_ini, fecha_fin),
    FOREIGN KEY (nombre_parcela) REFERENCES parcela(nombre_parcela)
);

CREATE TABLE IF NOT EXISTS alerta (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha_emision   TIMESTAMPTZ NOT NULL,
    mensaje         TEXT NOT NULL,
    nombre_parcela  VARCHAR(255) NOT NULL,
    email_usuario   VARCHAR(255) NOT NULL,
    FOREIGN KEY (nombre_parcela) REFERENCES parcela(nombre_parcela),
    FOREIGN KEY (email_usuario)  REFERENCES usuario(email_usuario)
);

-- ============================================================
-- ASOCIACIONES (Tablas Intermedias M:N)
-- ============================================================

CREATE TABLE IF NOT EXISTS usuario_rol_campo (
    email_usuario VARCHAR(255) NOT NULL,
    nombre_rol    VARCHAR(100) NOT NULL,
    nombre_campo  VARCHAR(255) NOT NULL,
    PRIMARY KEY (email_usuario, nombre_rol, nombre_campo),
    FOREIGN KEY (email_usuario) REFERENCES usuario(email_usuario),
    FOREIGN KEY (nombre_rol)    REFERENCES rol(nombre_rol),
    FOREIGN KEY (nombre_campo)  REFERENCES campo(nombre_campo)
);

CREATE TABLE IF NOT EXISTS parcela_imagen_satelital (
    id_imagen       VARCHAR(255) NOT NULL,
    nombre_parcela  VARCHAR(255) NOT NULL,
    indice_ndvi     FLOAT,        -- Normalized Difference Vegetation Index (-1 a 1)
    indice_ndmi     FLOAT,        -- Normalized Difference Moisture Index (-1 a 1)
    PRIMARY KEY (id_imagen, nombre_parcela),
    FOREIGN KEY (id_imagen)      REFERENCES imagen_satelital(id_imagen),
    FOREIGN KEY (nombre_parcela) REFERENCES parcela(nombre_parcela)
);

CREATE TABLE IF NOT EXISTS registro_cultivo (
    nombre_parcela  VARCHAR(255) NOT NULL,
    nombre_cultivo  VARCHAR(255) NOT NULL,
    fecha_siembra   TIMESTAMPTZ NOT NULL,
    fecha_cosecha   TIMESTAMPTZ,
    PRIMARY KEY (nombre_parcela, nombre_cultivo, fecha_siembra),
    FOREIGN KEY (nombre_parcela) REFERENCES parcela(nombre_parcela),
    FOREIGN KEY (nombre_cultivo) REFERENCES cultivo(nombre_cultivo)
);

CREATE TABLE IF NOT EXISTS sensor_parcela (
    nombre_codigo_sensor VARCHAR(255) NOT NULL,
    nombre_parcela       VARCHAR(255) NOT NULL,
    nombre_campo         VARCHAR(255) NOT NULL,
    fecha_instalacion    TIMESTAMPTZ NOT NULL,
    fecha_retiro         TIMESTAMPTZ,
    PRIMARY KEY (nombre_codigo_sensor, nombre_parcela, fecha_instalacion),
    FOREIGN KEY (nombre_codigo_sensor) REFERENCES sensor(nombre_codigo_sensor),
    FOREIGN KEY (nombre_parcela)       REFERENCES parcela(nombre_parcela),
    FOREIGN KEY (nombre_campo)         REFERENCES campo(nombre_campo)
);

CREATE TABLE IF NOT EXISTS prediccion (
    id            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha_emision TIMESTAMPTZ NOT NULL,
    resultado     TEXT NOT NULL,
    fecha_ini     TIMESTAMPTZ NOT NULL,
    fecha_fin     TIMESTAMPTZ NOT NULL,
    nombre_regla  VARCHAR(255) NOT NULL,
    nombre_campo  VARCHAR(255) NOT NULL,
    FOREIGN KEY (nombre_regla, nombre_campo)
        REFERENCES regla(nombre_regla, nombre_campo),
    FOREIGN KEY (fecha_ini, fecha_fin)
        REFERENCES ventana_temporal(fecha_ini, fecha_fin)
);
