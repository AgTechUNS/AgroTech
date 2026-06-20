import { Campo, Parcela, Regla, Sensor, Agricultor } from "@/lib/types";

const ADMIN1 = "test@agtechuns.com";
const ADMIN2 = "admin2@ejemplo.com";

export const SEED_CAMPOS: Campo[] = [
  {
    nombreCampo: "Campo Los Pinos",
    descripcionCampo: "Establecimiento norte destinado a cultivos rotativos",
    coordenadasCampo: JSON.stringify({
      type: "Polygon",
      coordinates: [[[-62.5, -38.0], [-62.3, -38.0], [-62.3, -37.8], [-62.5, -37.8], [-62.5, -38.0]]],
    }),
    adminEmail: ADMIN1,
  },
  {
    nombreCampo: "Campo El Ombú",
    descripcionCampo: "Campo sur con riego por goteo",
    coordenadasCampo: JSON.stringify({
      type: "Polygon",
      coordinates: [[[-62.8, -38.5], [-62.6, -38.5], [-62.6, -38.3], [-62.8, -38.3], [-62.8, -38.5]]],
    }),
    adminEmail: ADMIN1,
  },
  {
    nombreCampo: "Campo La Esperanza",
    descripcionCampo: "Campo este con sistema de pivote central",
    coordenadasCampo: JSON.stringify({
      type: "Polygon",
      coordinates: [[[-62.1, -37.5], [-61.9, -37.5], [-61.9, -37.3], [-62.1, -37.3], [-62.1, -37.5]]],
    }),
    adminEmail: ADMIN2,
  },
  {
    nombreCampo: "Campo Santa Rosa",
    descripcionCampo: "Campo oeste destinado a pasturas",
    coordenadasCampo: JSON.stringify({
      type: "Polygon",
      coordinates: [[[-63.0, -38.2], [-62.8, -38.2], [-62.8, -38.0], [-63.0, -38.0], [-63.0, -38.2]]],
    }),
    adminEmail: ADMIN2,
  },
];

export const SEED_PARCELAS: Parcela[] = [
  {
    nombreParcela: "Lote A",
    nombreCampo: "Campo Los Pinos",
    descripcionParcela: "Parcela norte destinada a trigo",
    nombreCultivo: "Trigo",
    variedad: "ACA 303",
    coordenadasParcela: JSON.stringify({
      type: "Polygon",
      coordinates: [[[-62.45, -37.9], [-62.35, -37.9], [-62.35, -37.85], [-62.45, -37.85], [-62.45, -37.9]]],
    }),
    adminEmail: ADMIN1,
  },
  {
    nombreParcela: "Lote B",
    nombreCampo: "Campo Los Pinos",
    descripcionParcela: "Parcela sur con riego",
    nombreCultivo: "Maíz",
    variedad: "DK 390",
    coordenadasParcela: JSON.stringify({
      type: "Polygon",
      coordinates: [[[-62.45, -37.95], [-62.35, -37.95], [-62.35, -37.9], [-62.45, -37.9], [-62.45, -37.95]]],
    }),
    adminEmail: ADMIN1,
  },
  {
    nombreParcela: "Lote A",
    nombreCampo: "Campo La Esperanza",
    descripcionParcela: "Parcela principal con pivote",
    nombreCultivo: "Avena",
    variedad: "Cristal",
    coordenadasParcela: JSON.stringify({
      type: "Polygon",
      coordinates: [[[-62.05, -37.45], [-61.95, -37.45], [-61.95, -37.35], [-62.05, -37.35], [-62.05, -37.45]]],
    }),
    adminEmail: ADMIN2,
  },
];

export const SEED_REGLAS: Regla[] = [
  { metrica: "temperatura", operador: ">=", valor: 38.0, adminEmail: ADMIN1 },
  { metrica: "humedad_suelo", operador: "<=", valor: 20.0, adminEmail: ADMIN1 },
  { metrica: "precipitacion", operador: "<", valor: 5.0, adminEmail: ADMIN1 },
  { metrica: "viento", operador: ">=", valor: 50.0, adminEmail: ADMIN1 },
  { metrica: "ndvi", operador: "<=", valor: 0.3, adminEmail: ADMIN1 },
  { metrica: "temperatura", operador: ">=", valor: 35.0, adminEmail: ADMIN2 },
  { metrica: "humedad_suelo", operador: "<=", valor: 25.0, adminEmail: ADMIN2 },
];

export const SEED_SENSORES: Sensor[] = [
  { deviceId: "SNS-001", nombreCampo: "Campo Los Pinos", nombreParcela: "Lote A", tipo: "temperatura_humedad", activo: true, adminEmail: ADMIN1 },
  { deviceId: "SNS-002", nombreCampo: "Campo Los Pinos", nombreParcela: "Lote B", tipo: "temperatura_humedad", activo: true, adminEmail: ADMIN1 },
  { deviceId: "SNS-003", nombreCampo: "Campo Los Pinos", nombreParcela: "Lote A", tipo: "ph", activo: false, adminEmail: ADMIN1 },
  { deviceId: "SNS-004", nombreCampo: "Campo El Ombú", nombreParcela: "Lote A", tipo: "temperatura_humedad", activo: true, adminEmail: ADMIN1 },
  { deviceId: "SNS-005", nombreCampo: "Campo La Esperanza", nombreParcela: "Lote A", tipo: "temperatura_humedad", activo: true, adminEmail: ADMIN2 },
  { deviceId: "SNS-006", nombreCampo: "Campo La Esperanza", nombreParcela: "Lote A", tipo: "lluvia", activo: true, adminEmail: ADMIN2 },
];

export const SEED_AGRICULTORES: Agricultor[] = [
  { email: "test@agtechuns.com", nombre: "Admin", password: "12345678", rol: "ADMIN" },
  { email: "admin2@ejemplo.com", nombre: "Admin Dos", password: "12345678", rol: "ADMIN" },
  { email: "agricultor@ejemplo.com", nombre: "Agricultor Uno", password: "12345678", rol: "agricultor", adminEmail: ADMIN1 },
];
