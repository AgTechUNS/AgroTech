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
}

export interface Parcela {
  nombreParcela: string;
  nombreCampo: string;
  descripcionParcela?: string;
  nombreCultivo: string | null;
  coordenadasParcela: string;
}

export interface Cultivo {
  nombreCultivo: string;
  umbralHumedadMinima: number;
}

export interface Regla {
  metrica: string;
  operador: string;
  valor: number;
}

export interface Usuario {
  email: string;
  rol: "ADMIN" | "AGRONOMO" | "PRODUCTOR";
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
  nombreSensor: string;
  tipo: string;
  credencialesMqtt?: string;
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
  role: "ADMIN" | "AGRONOMO" | "PRODUCTOR";
  name?: string;
  iat: number;
  exp: number;
}
