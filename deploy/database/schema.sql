-- AgroTech - Esquema de Base de Datos Relacional
-- PostgreSQL (compatible Neon)

-- Enum para roles de usuario
DO $$ BEGIN
  CREATE TYPE rol_usuario AS ENUM ('ADMIN', 'AGRONOMO', 'PRODUCTOR');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

-- ============================================================
-- TABLAS
-- ============================================================

-- 1. Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    email         VARCHAR(255) PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,
    rol           rol_usuario  NOT NULL
);

-- 2. Cultivos (catálogo)
CREATE TABLE IF NOT EXISTS cultivos (
    nombre                    VARCHAR(100) PRIMARY KEY,
    umbral_humedad_minima     FLOAT        NOT NULL,
    umbral_temperatura_maxima FLOAT
);

-- 3. Campos
CREATE TABLE IF NOT EXISTS campos (
    nombre       VARCHAR(100) PRIMARY KEY,
    descripcion  TEXT,
    coordenadas  TEXT NOT NULL  -- GeoJSON Polygon
);

-- 4. Parcelas (relacionadas a Campos y opcionalmente a Cultivos)
CREATE TABLE IF NOT EXISTS parcelas (
    nombre         VARCHAR(100) NOT NULL,
    campo_nombre   VARCHAR(100) NOT NULL,
    coordenadas    TEXT         NOT NULL,  -- GeoJSON Polygon
    descripcion    TEXT,
    cultivo_nombre VARCHAR(100),

    PRIMARY KEY (nombre, campo_nombre),
    FOREIGN KEY (campo_nombre)   REFERENCES campos(nombre)   ON DELETE CASCADE,
    FOREIGN KEY (cultivo_nombre) REFERENCES cultivos(nombre)  ON DELETE SET NULL
);

-- 5. Reglas (umbrales agroclimáticos)
CREATE TABLE IF NOT EXISTS reglas (
    id       INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    metrica  VARCHAR(50)  NOT NULL,
    operador VARCHAR(10)  NOT NULL,
    valor    FLOAT        NOT NULL
);
