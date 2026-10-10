import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'

const radicados = [
  {
    numero: '2026-P-1',
    tipo: 'PETICION',
    asunto: 'Petición de copia de resolución',
    descripcion: '',
    remitente: 'Ana Gómez',
    estado: 'RADICADO',
    fecha_radicacion: '2026-03-02',
    fecha_vencimiento: '2026-03-17',
  },
  {
    numero: '2026-Q-1',
    tipo: 'QUEJA',
    asunto: 'Queja por demora',
    descripcion: '',
    remitente: null,
    estado: 'EN_TRAMITE',
    fecha_radicacion: '2026-03-03',
    fecha_vencimiento: '2026-03-18',
  },
]

function mockFetch(respuesta: unknown) {
  return vi.spyOn(globalThis, 'fetch').mockResolvedValue(
    new Response(JSON.stringify(respuesta), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }),
  )
}

describe('App', () => {
  afterEach(() => vi.restoreAllMocks())

  it('lista los radicados al cargar', async () => {
    mockFetch({ total: 2, items: radicados })
    render(<App />)
    expect(await screen.findByText('2026-P-1')).toBeInTheDocument()
    expect(screen.getByText('Queja por demora')).toBeInTheDocument()
    expect(screen.getByTestId('contador')).toHaveTextContent('2')
  })

  it('muestra guion cuando no hay remitente', async () => {
    mockFetch({ total: 2, items: radicados })
    render(<App />)
    await screen.findByText('2026-Q-1')
    expect(screen.getByText('—')).toBeInTheDocument()
  })
})
