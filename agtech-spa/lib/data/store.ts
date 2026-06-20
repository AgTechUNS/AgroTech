import fs from "fs";
import path from "path";
import { Campo, Cultivo, Parcela, Regla, Sensor, Gateway, Usuario, CatalogoCultivo } from "@/lib/types";
import { CATALOGO_CULTIVOS } from "./catalogo";
import { SEED_CAMPOS, SEED_PARCELAS, SEED_REGLAS, SEED_SENSORES, SEED_USUARIOS } from "./seed";

const DATA_DIR = path.resolve(process.cwd(), "..", ".data");
const CAMPOS_PATH = path.join(DATA_DIR, "campos.json");
const CULTIVOS_PATH = path.join(DATA_DIR, "cultivos.json");
const PARCELAS_PATH = path.join(DATA_DIR, "parcelas.json");
const REGLAS_PATH = path.join(DATA_DIR, "reglas.json");
const SENSORES_PATH = path.join(DATA_DIR, "sensores.json");
const USUARIOS_PATH = path.join(DATA_DIR, "usuarios.json");

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

export function getAdminEmail(email: string): string {
  const user = findUsuario(email);
  if (!user) return email;
  if (user.rol === "ADMIN") return user.email;
  return user.adminEmail ?? email;
}

// --- Campos ---

export function readCampos(adminEmail?: string): Campo[] {
  const all = readFile(CAMPOS_PATH, SEED_CAMPOS);
  if (adminEmail) return all.filter((c) => c.adminEmail === adminEmail);
  return all;
}

export function addCampo(campo: Campo): void {
  const campos = readCampos();
  campos.push(campo);
  writeFile(CAMPOS_PATH, campos);
}

export function updateCampo(nombreCampo: string, data: Partial<Campo>): void {
  const campos = readCampos();
  const idx = campos.findIndex((c) => c.nombreCampo === nombreCampo);
  if (idx === -1) return;
  campos[idx] = { ...campos[idx], ...data };
  writeFile(CAMPOS_PATH, campos);
}

export function deleteCampo(nombreCampo: string): void {
  const campos = readCampos();
  writeFile(CAMPOS_PATH, campos.filter((c) => c.nombreCampo !== nombreCampo));
}

// --- Cultivos ---

export function readCultivos(adminEmail?: string): Cultivo[] {
  const all = readFile<Cultivo>(CULTIVOS_PATH, []);
  if (adminEmail) return all.filter((c) => c.adminEmail === adminEmail);
  return all;
}

export function addCultivo(cultivo: Cultivo): void {
  const cultivos = readCultivos();
  cultivos.push(cultivo);
  writeFile(CULTIVOS_PATH, cultivos);
}

export function readCatalogo(): CatalogoCultivo[] {
  return CATALOGO_CULTIVOS;
}

// --- Parcelas ---

export function readParcelas(adminEmail: string, nombreCampo?: string): Parcela[] {
  let all = readFile(PARCELAS_PATH, SEED_PARCELAS).filter((p) => p.adminEmail === adminEmail);
  if (nombreCampo) all = all.filter((p) => p.nombreCampo === nombreCampo);
  return all;
}

export function addParcela(parcela: Parcela): void {
  const parcelas = readFile(PARCELAS_PATH, SEED_PARCELAS);
  parcelas.push(parcela);
  writeFile(PARCELAS_PATH, parcelas);
}

export function updateParcela(nombreCampo: string, nombreParcela: string, data: Partial<Parcela>): void {
  const parcelas = readFile(PARCELAS_PATH, SEED_PARCELAS);
  const idx = parcelas.findIndex((p) => p.nombreCampo === nombreCampo && p.nombreParcela === nombreParcela);
  if (idx === -1) return;
  parcelas[idx] = { ...parcelas[idx], ...data };
  writeFile(PARCELAS_PATH, parcelas);
}

export function deleteParcela(nombreCampo: string, nombreParcela: string): void {
  const parcelas = readFile(PARCELAS_PATH, SEED_PARCELAS);
  writeFile(PARCELAS_PATH, parcelas.filter((p) => p.nombreCampo !== nombreCampo || p.nombreParcela !== nombreParcela));
}

export function deleteParcelasByCampo(nombreCampo: string): void {
  const parcelas = readFile(PARCELAS_PATH, SEED_PARCELAS);
  writeFile(PARCELAS_PATH, parcelas.filter((p) => p.nombreCampo !== nombreCampo));
}

// --- Reglas ---

function normalizarRegla(r: Regla): Regla {
  return { ...r, camposAsignados: r.camposAsignados ?? [] };
}

export function readReglas(adminEmail?: string): Regla[] {
  const all = readFile(REGLAS_PATH, SEED_REGLAS).map(normalizarRegla);
  if (adminEmail) return all.filter((r) => r.adminEmail === adminEmail);
  return all;
}

export function getRegla(id: string, adminEmail?: string): Regla | undefined {
  const r = readFile(REGLAS_PATH, SEED_REGLAS).find((r) => r.id === id);
  return r ? normalizarRegla(r) : undefined;
}

export function addRegla(regla: Regla): void {
  const reglas = readReglas();
  reglas.push(regla);
  writeFile(REGLAS_PATH, reglas);
}

export function updateRegla(id: string, data: Partial<Regla>): void {
  const reglas = readReglas();
  const idx = reglas.findIndex((r) => r.id === id);
  if (idx === -1) return;
  reglas[idx] = { ...reglas[idx], ...data };
  writeFile(REGLAS_PATH, reglas);
}

export function deleteRegla(id: string): void {
  const reglas = readReglas();
  writeFile(REGLAS_PATH, reglas.filter((r) => r.id !== id));
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

function readSensoresStore(): SensorStore {
  initSensorStore();
  const raw = fs.readFileSync(SENSORES_PATH, "utf-8");
  return JSON.parse(raw) as SensorStore;
}

export function readSensores(adminEmail?: string): SensorStore {
  const store = readSensoresStore();
  if (adminEmail) {
    return {
      gateways: store.gateways.filter((g) => !g.adminEmail || g.adminEmail === adminEmail),
      sensors: store.sensors.filter((s) => !s.adminEmail || s.adminEmail === adminEmail),
    };
  }
  return store;
}

export function writeSensores(store: SensorStore): void {
  ensureDir();
  fs.writeFileSync(SENSORES_PATH, JSON.stringify(store, null, 2), "utf-8");
}

export function readSensoresPorCampo(adminEmail: string, nombreCampo: string): Sensor[] {
  return readSensores(adminEmail).sensors.filter((s) => s.nombreCampo === nombreCampo);
}

export function readSensoresPorParcela(adminEmail: string, nombreCampo: string, nombreParcela: string): Sensor[] {
  return readSensores(adminEmail).sensors.filter(
    (s) => s.nombreCampo === nombreCampo && s.nombreParcela === nombreParcela
  );
}

// --- Usuarios ---

export function readUsuarios(adminEmail?: string): Usuario[] {
  const all = readFile(USUARIOS_PATH, SEED_USUARIOS);
  if (adminEmail) {
    return all.filter(
      (a) => a.email === adminEmail || (a.rol !== "ADMIN" && a.adminEmail === adminEmail)
    );
  }
  return all;
}

export function addUsuario(usuario: Usuario): void {
  const list = readUsuarios();
  list.push(usuario);
  writeFile(USUARIOS_PATH, list);
}

export function updateUsuario(email: string, data: Partial<Usuario>): void {
  const list = readUsuarios();
  const idx = list.findIndex((a) => a.email === email);
  if (idx === -1) return;
  list[idx] = { ...list[idx], ...data };
  writeFile(USUARIOS_PATH, list);
}

export function deleteUsuario(email: string): void {
  const list = readUsuarios();
  writeFile(USUARIOS_PATH, list.filter((a) => a.email !== email));
}

export function findUsuario(email: string): Usuario | undefined {
  return readUsuarios().find((a) => a.email === email);
}
