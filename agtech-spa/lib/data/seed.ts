import { Campo, Cultivo, Parcela, Regla, Sensor } from "@/lib/types";

export const SEED_CAMPOS: Campo[] = [
  {
    nombreCampo: "Campo Los Pinos",
    descripcionCampo: "Establecimiento norte destinado a cultivos rotativos",
    coordenadasCampo: JSON.stringify({
      type: "Polygon",
      coordinates: [[[-62.5, -38.0], [-62.3, -38.0], [-62.3, -37.8], [-62.5, -37.8], [-62.5, -38.0]]],
    }),
  },
  {
    nombreCampo: "Campo El Ombú",
    descripcionCampo: "Campo sur con riego por goteo",
    coordenadasCampo: JSON.stringify({
      type: "Polygon",
      coordinates: [[[-62.8, -38.5], [-62.6, -38.5], [-62.6, -38.3], [-62.8, -38.3], [-62.8, -38.5]]],
    }),
  },
];

export const SEED_CULTIVOS: Cultivo[] = [
  { nombreCultivo: "Trigo", umbralHumedadMinima: 30.5 },
  { nombreCultivo: "Maíz", umbralHumedadMinima: 35.0 },
  { nombreCultivo: "Soja", umbralHumedadMinima: 28.0 },
  { nombreCultivo: "Girasol", umbralHumedadMinima: 25.0 },
  { nombreCultivo: "Cebada", umbralHumedadMinima: 32.0 },
];

export const SEED_PARCELAS: Parcela[] = [
  {
    nombreParcela: "Lote A",
    nombreCampo: "Campo Los Pinos",
    descripcionParcela: "Parcela norte destinada a trigo",
    nombreCultivo: "Trigo",
    coordenadasParcela: JSON.stringify({
      type: "Polygon",
      coordinates: [[[-62.45, -37.9], [-62.35, -37.9], [-62.35, -37.85], [-62.45, -37.85], [-62.45, -37.9]]],
    }),
  },
  {
    nombreParcela: "Lote B",
    nombreCampo: "Campo Los Pinos",
    descripcionParcela: "Parcela sur con riego",
    nombreCultivo: "Maíz",
    coordenadasParcela: JSON.stringify({
      type: "Polygon",
      coordinates: [[[-62.45, -37.95], [-62.35, -37.95], [-62.35, -37.9], [-62.45, -37.9], [-62.45, -37.95]]],
    }),
  },
];

export const SEED_REGLAS: Regla[] = [
  { metrica: "temperatura", operador: ">=", valor: 38.0 },
  { metrica: "humedad_suelo", operador: "<=", valor: 20.0 },
  { metrica: "precipitacion", operador: "<", valor: 5.0 },
  { metrica: "viento", operador: ">=", valor: 50.0 },
  { metrica: "ndvi", operador: "<=", valor: 0.3 },
];

export const SEED_SENSORES: Sensor[] = [
  { deviceId: "SNS-001", nombreCampo: "Campo Los Pinos", nombreParcela: "Lote A", tipo: "temperatura_humedad", activo: true },
  { deviceId: "SNS-002", nombreCampo: "Campo Los Pinos", nombreParcela: "Lote B", tipo: "temperatura_humedad", activo: true },
  { deviceId: "SNS-003", nombreCampo: "Campo Los Pinos", nombreParcela: "Lote A", tipo: "ph", activo: false },
  { deviceId: "SNS-004", nombreCampo: "Campo El Ombú", nombreParcela: "Lote A", tipo: "temperatura_humedad", activo: true },
];
