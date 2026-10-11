export const TIPOS = [
  'PETICION',
  'QUEJA',
  'RECLAMO',
  'SUGERENCIA',
  'DENUNCIA',
  'CONSULTA',
  'INFORMACION',
] as const

export type TipoPQRSDF = (typeof TIPOS)[number]

export interface Radicado {
  numero: string
  tipo: TipoPQRSDF
  asunto: string
  descripcion: string
  remitente: string | null
  estado: string
  fecha_radicacion: string
  fecha_vencimiento: string
  motivo_anulacion?: string | null
  fecha_anulacion?: string | null
}

export interface ListaRadicados {
  total: number
  items: Radicado[]
}

export interface NuevoRadicado {
  tipo: TipoPQRSDF
  asunto: string
  descripcion: string
  remitente: string
}

export interface RadicadoAnular {
  motivo: string
}
