import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { anularRadicado, crearRadicado, listarRadicados } from './api'
import { TIPOS, type NuevoRadicado, type Radicado } from './types'
import './App.css'

const VACIO: NuevoRadicado = { tipo: 'PETICION', asunto: '', descripcion: '', remitente: '' }

export default function App() {
  const [items, setItems] = useState<Radicado[]>([])
  const [totalGeneral, setTotalGeneral] = useState(0)
  const [busqueda, setBusqueda] = useState('')
  const [form, setForm] = useState<NuevoRadicado>(VACIO)
  const [mensaje, setMensaje] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const cargar = useCallback(async (q?: string) => {
    try {
      const datos = await listarRadicados(q)
      setItems(datos.items)
      if (!q) setTotalGeneral(datos.total)
      setError(null)
    } catch (e) {
      setError((e as Error).message)
    }
  }, [])

  useEffect(() => {
    void cargar()
  }, [cargar])

  const buscar = (e: FormEvent) => {
    e.preventDefault()
    void cargar(busqueda.trim() || undefined)
  }

  const radicar = async (e: FormEvent) => {
    e.preventDefault()
    try {
      const nuevo = await crearRadicado(form)
      setMensaje(`Radicado ${nuevo.numero} creado. Vence el ${nuevo.fecha_vencimiento}.`)
      setForm(VACIO)
      await cargar()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  const anular = async (numero: string) => {
    const motivo = window.prompt('Ingrese el motivo de anulación (mínimo 10 caracteres):')
    if (motivo === null) return
    const motivoLimpio = motivo.trim()
    if (!motivoLimpio) return
    try {
      await anularRadicado(numero, motivoLimpio)
      setMensaje(`Radicado ${numero} anulado exitosamente.`)
      setError(null)
      await cargar(busqueda.trim() || undefined)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <main className="app">
      <header>
        <h1>Radicación de PQRSDF</h1>
        <p className="sub">Mini-SGDEA · repo de prueba del pipeline con agentes</p>
      </header>

      <section className="panel">
        <h2>Nuevo radicado</h2>
        <form onSubmit={radicar} className="formulario">
          <label>
            Tipo
            <select
              value={form.tipo}
              onChange={(e) => setForm({ ...form, tipo: e.target.value as NuevoRadicado['tipo'] })}
            >
              {TIPOS.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
          <label>
            Asunto
            <input
              value={form.asunto}
              onChange={(e) => setForm({ ...form, asunto: e.target.value })}
              required
            />
          </label>
          <label>
            Remitente
            <input
              value={form.remitente}
              onChange={(e) => setForm({ ...form, remitente: e.target.value })}
            />
          </label>
          <label className="ancho">
            Descripción
            <textarea
              value={form.descripcion}
              onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
            />
          </label>
          <button type="submit">Radicar</button>
        </form>
        {mensaje && <p className="ok">{mensaje}</p>}
      </section>

      <section className="panel">
        <form onSubmit={buscar} className="busqueda">
          <input
            aria-label="Buscar"
            placeholder="Buscar por asunto o número"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
          <button type="submit">Buscar</button>
        </form>
        <p className="contador" data-testid="contador">
          Mostrando {totalGeneral} radicados
        </p>
        {error && <p className="error">{error}</p>}
        <table>
          <thead>
            <tr>
              <th>Número</th>
              <th>Tipo</th>
              <th>Asunto</th>
              <th>Remitente</th>
              <th>Estado</th>
              <th>Vence</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((r) => (
              <tr key={r.numero}>
                <td className="mono">{r.numero}</td>
                <td>{r.tipo}</td>
                <td>{r.asunto}</td>
                <td>{r.remitente ?? '—'}</td>
                <td>{r.estado}</td>
                <td>{r.fecha_vencimiento}</td>
                <td>
                  <button
                    type="button"
                    className="btn-anular"
                    onClick={() => void anular(r.numero)}
                    disabled={r.estado === 'ANULADO' || r.estado === 'RESPONDIDO'}
                  >
                    Anular
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  )
}
