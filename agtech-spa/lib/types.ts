export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

export interface Pagination {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: Pagination;
}

export interface Campo {
  nombreCampo: string;
  descripcionCampo?: string;
  coordenadasCampo: string;
  adminEmail: string;
}

export interface Parcela {
  nombreParcela: string;
  nombreCampo: string;
  descripcionParcela?: string;
  nombreCultivo: string | null;
  variedad: string | null;
  coordenadasParcela: string;
  adminEmail: string;
}

export interface Cultivo {
  nombreCultivo: string;
  variedad: string;
  adminEmail: string;
}

export interface CatalogoCultivo {
  nombreCultivo: string;
  variedad: string;
}

export interface Regla {
  metrica: string;
  operador: string;
  valor: number;
  adminEmail: string;
}

export interface Agricultor {
  email: string;
  nombre: string;
  password: string;
  rol: "agricultor" | "ADMIN";
  adminEmail?: string;
}

export interface Usuario {
  email: string;
  rol: "ADMIN" | "AGRONOMO" | "PRODUCTOR";
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface WeatherResponse {
  temperature_celsius: number;
  humidity_percent: number;
  timestamp: string;
  latitude: number;
  longitude: number;
}

export interface AlertaRecomendacion {
  tipo: "ALERTA_TIEMPO_REAL" | "RECOMENDACION_BATCH";
  fechaEmision: string;
  mensaje: string;
  nombreParcela: string;
  emailUsuario?: string;
}

export interface RegistroCultivo {
  nombreCultivo: string;
  fechaSiembra: string;
  fechaCosecha?: string;
  observaciones?: string;
}

export interface Sensor {
  deviceId: string;
  nombreCampo: string;
  nombreParcela: string;
  tipo: "temperatura_humedad" | "ph" | "lluvia";
  activo: boolean;
  adminEmail: string;
}

export interface Gateway {
  gatewayId: string;
  nombreCampo: string;
  adminEmail: string;
}

export interface Lectura {
  sensorId: string;
  timestamp: string;
  temperatura: number | null;
  humedad: number | null;
}

export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface JwtPayload {
  sub: string;
  email: string;
  role: "ADMIN" | "agricultor";
  name?: string;
  adminEmail?: string;
  iat: number;
  exp: number;
}
