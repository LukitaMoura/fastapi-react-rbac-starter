import { useCallback, useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Plus, Search } from 'lucide-react';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { Botao, Card, Erro, Prioridade, STATUS_LABEL, StatusBadge, dataHora } from '../components/ui';

const POR_PAGINA = 10;

function NovoChamado({ onCriado, onCancelar }) {
  const [form, setForm] = useState({ titulo: '', categoria: 'Manutenção', prioridade: 'media', descricao: '' });
  const [erro, setErro] = useState('');
  const set = (campo) => (e) => setForm({ ...form, [campo]: e.target.value });

  async function salvar(e) {
    e.preventDefault();
    try {
      onCriado(await api('/chamados', { method: 'POST', body: form }));
    } catch (err) {
      setErro(err.message);
    }
  }

  const campo = 'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500';
  return (
    <Card>
      <form onSubmit={salvar} className="grid gap-4 md:grid-cols-3">
        <label className="md:col-span-3">
          <span className="text-sm font-medium text-slate-700">Título</span>
          <input required minLength={3} value={form.titulo} onChange={set('titulo')} className={campo} />
        </label>
        <label>
          <span className="text-sm font-medium text-slate-700">Categoria</span>
          <select value={form.categoria} onChange={set('categoria')} className={campo}>
            {['Manutenção', 'TI', 'Limpeza', 'Compras', 'RH'].map((c) => <option key={c}>{c}</option>)}
          </select>
        </label>
        <label>
          <span className="text-sm font-medium text-slate-700">Prioridade</span>
          <select value={form.prioridade} onChange={set('prioridade')} className={campo}>
            <option value="baixa">Baixa</option>
            <option value="media">Média</option>
            <option value="alta">Alta</option>
            <option value="critica">Crítica</option>
          </select>
        </label>
        <label className="md:col-span-3">
          <span className="text-sm font-medium text-slate-700">Descrição</span>
          <textarea rows={3} value={form.descricao} onChange={set('descricao')} className={campo} />
        </label>
        <div className="flex items-center gap-2 md:col-span-3">
          <Botao type="submit">Abrir chamado</Botao>
          <Botao type="button" variante="secundario" onClick={onCancelar}>Cancelar</Botao>
          <Erro mensagem={erro} />
        </div>
      </form>
    </Card>
  );
}

export default function Chamados() {
  const { pode } = useAuth();
  const [params, setParams] = useSearchParams();
  const [dados, setDados] = useState({ total: 0, itens: [] });
  const [erro, setErro] = useState('');
  const [novo, setNovo] = useState(false);
  const [busca, setBusca] = useState(params.get('busca') || '');

  const status = params.get('status') || '';
  const pagina = Number(params.get('pagina') || 1);

  const carregar = useCallback(() => {
    api('/chamados', { params: { status, busca: params.get('busca'), pagina, por_pagina: POR_PAGINA } })
      .then(setDados)
      .catch((e) => setErro(e.message));
  }, [status, pagina, params]);

  useEffect(carregar, [carregar]);

  const filtrar = (mudancas) => {
    const p = new URLSearchParams(params);
    Object.entries({ pagina: 1, ...mudancas }).forEach(([k, v]) => (v ? p.set(k, v) : p.delete(k)));
    setParams(p);
  };
  const paginas = Math.max(1, Math.ceil(dados.total / POR_PAGINA));

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-slate-900">Chamados</h1>
        {pode('chamados.criar') && !novo && (
          <Botao onClick={() => setNovo(true)} className="flex items-center gap-2"><Plus size={16} /> Novo chamado</Botao>
        )}
      </div>

      {novo && <NovoChamado onCancelar={() => setNovo(false)} onCriado={() => { setNovo(false); carregar(); }} />}

      <div className="flex flex-wrap gap-3">
        <form onSubmit={(e) => { e.preventDefault(); filtrar({ busca }); }} className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Buscar pelo título"
            className="rounded-lg border border-slate-300 py-2 pl-9 pr-3 text-sm outline-none focus:border-indigo-500" />
        </form>
        <select value={status} onChange={(e) => filtrar({ status: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
          <option value="">Todos os status</option>
          {Object.entries(STATUS_LABEL).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      </div>

      <Erro mensagem={erro} />

      <Card className="overflow-x-auto p-0">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">#</th>
              <th className="px-4 py-3">Título</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Prioridade</th>
              <th className="px-4 py-3">Solicitante</th>
              <th className="px-4 py-3">Aberto em</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {dados.itens.map((c) => (
              <tr key={c.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 tabular-nums text-slate-500">{c.id}</td>
                <td className="px-4 py-3">
                  <Link to={`/chamados/${c.id}`} className="font-medium text-indigo-700 hover:underline">{c.titulo}</Link>
                  <p className="text-xs text-slate-500">{c.categoria}</p>
                </td>
                <td className="px-4 py-3"><StatusBadge status={c.status} /></td>
                <td className="px-4 py-3"><Prioridade valor={c.prioridade} /></td>
                <td className="px-4 py-3 text-slate-600">{c.solicitante.nome}</td>
                <td className="px-4 py-3 text-slate-500">{dataHora(c.criado_em)}</td>
              </tr>
            ))}
            {dados.itens.length === 0 && (
              <tr><td colSpan={6} className="px-4 py-10 text-center text-slate-400">Nenhum chamado encontrado.</td></tr>
            )}
          </tbody>
        </table>
      </Card>

      <div className="flex items-center justify-between text-sm text-slate-600">
        <span>{dados.total} chamado(s)</span>
        <div className="flex items-center gap-2">
          <Botao variante="secundario" disabled={pagina <= 1} onClick={() => filtrar({ status, busca: params.get('busca'), pagina: pagina - 1 })}>Anterior</Botao>
          <span>{pagina} / {paginas}</span>
          <Botao variante="secundario" disabled={pagina >= paginas} onClick={() => filtrar({ status, busca: params.get('busca'), pagina: pagina + 1 })}>Próxima</Botao>
        </div>
      </div>
    </div>
  );
}
