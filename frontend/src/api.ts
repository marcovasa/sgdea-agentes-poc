import type { ListaRadicados, NuevoRadicado, Radicado } from './types'

declare global {
  interface Window {
    __CONFIG__?: { API_URL?: string }
  }
}

const base = () => (window.__CONFIG__?.API_URL ?? '').replace(/\/$/, '')

async function solicitar<T>(ruta: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${base()}${ruta}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!r.ok) {
    const detalle = await r.text()
    throw new Error(`Error ${r.status}: ${detalle}`)
  }
  return r.json() as Promise<T>
}

export function listarRadicados(q?: string): Promise<ListaRadicados> {
  const params = q ? `?q=${encodeURIComponent(q)}` : ''
  return solicitar<ListaRadicados>(`/api/radicados${params}`)
}

export function crearRadicado(datos: NuevoRadicado): Promise<Radicado> {
  return solicitar<Radicado>('/api/radicados', {
    method: 'POST',
    body: JSON.stringify(datos),
  })
}
