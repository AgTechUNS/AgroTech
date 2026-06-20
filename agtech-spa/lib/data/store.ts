import fs from "fs";
import path from "path";
import { Campo, Cultivo, Parcela, Regla, Sensor, Gateway } from "@/lib/types";
import { SEED_CAMPOS, SEED_CULTIVOS, SEED_PARCELAS, SEED_REGLAS, SEED_SENSORES } from "./seed";

const DATA_DIR = path.resolve(process.cwd(), "..", ".data");
const CAMPOS_PATH = path.join(DATA_DIR, "campos.json");
const CULTIVOS_PATH = path.join(DATA_DIR, "cultivos.json");
const PARCELAS_PATH = path.join(DATA_DIR, "parcelas.json");
const REGLAS_PATH = path.join(DATA_DIR, "reglas.json");
const SENSORES_PATH = path.join(DATA_DIR, "sensores.json");

function ensureDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function initFile(filePath: string, seedData: unknown[]) {
  ensureDir();
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, JSON.stringify(seedData, null, 2), "utf-8");
  }
}

function readFile<T>(filePath: string, seedData: T[]): T[] {
  initFile(filePath, seedData);
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as T[];
}

function writeFile<T>(filePath: string, data: T[]): void {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf-8");
}

// --- Campos ---

export function readCampos(): Campo[] {
  return readFile(CAMPOS_PATH, SEED_CAMPOS);
}

export function addCampo(campo: Campo): void {
  const campos = readCampos();
  campos.push(campo);
  writeFile(CAMPOS_PATH, campos);
}

// --- Cultivos ---

export function readCultivos(): Cultivo[] {
  return readFile(CULTIVOS_PATH, SEED_CULTIVOS);
}

export function addCultivo(cultivo: Cultivo): void {
  const cultivos = readCultivos();
  cultivos.push(cultivo);
  writeFile(CULTIVOS_PATH, cultivos);
}

// --- Parcelas ---

export function readParcelas(nombreCampo: string): Parcela[] {
  return readFile(PARCELAS_PATH, SEED_PARCELAS).filter(
    (p) => p.nombreCampo === nombreCampo
  );
}

export function addParcela(parcela: Parcela): void {
  const parcelas = readFile(PARCELAS_PATH, SEED_PARCELAS);
  parcelas.push(parcela);
  writeFile(PARCELAS_PATH, parcelas);
}

// --- Reglas ---

export function readReglas(): Regla[] {
  return readFile(REGLAS_PATH, SEED_REGLAS);
}

export function addRegla(regla: Regla): void {
  const reglas = readReglas();
  reglas.push(regla);
  writeFile(REGLAS_PATH, reglas);
}

// --- Sensores ---

interface SensorStore {
  gateways: Gateway[];
  sensors: Sensor[];
}

function initSensorStore(): void {
  ensureDir();
  if (!fs.existsSync(SENSORES_PATH)) {
    const seed: SensorStore = {
      gateways: [],
      sensors: SEED_SENSORES,
    };
    fs.writeFileSync(SENSORES_PATH, JSON.stringify(seed, null, 2), "utf-8");
  }
}

export function readSensores(): SensorStore {
  initSensorStore();
  const raw = fs.readFileSync(SENSORES_PATH, "utf-8");
  return JSON.parse(raw) as SensorStore;
}

export function writeSensores(store: SensorStore): void {
  ensureDir();
  fs.writeFileSync(SENSORES_PATH, JSON.stringify(store, null, 2), "utf-8");
}

export function readSensoresPorCampo(nombreCampo: string): Sensor[] {
  return readSensores().sensors.filter((s) => s.nombreCampo === nombreCampo);
}

export function readSensoresPorParcela(nombreCampo: string, nombreParcela: string): Sensor[] {
  return readSensores().sensors.filter(
    (s) => s.nombreCampo === nombreCampo && s.nombreParcela === nombreParcela
  );
}
