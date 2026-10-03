export const STATUS_LABEL = {
  aberto: 'Aberto',
  em_andamento: 'Em andamento',
  aguardando: 'Aguardando',
  resolvido: 'Resolvido',
  fechado: 'Fechado',
  cancelado: 'Cancelado',
};

const STATUS_COR = {
  aberto: 'bg-sky-100 text-sky-800',
  em_andamento: 'bg-amber-100 text-amber-800',
  aguardando: 'bg-violet-100 text-violet-800',
  resolvido: 'bg-emerald-100 text-emerald-800',
  fechado: 'bg-slate-200 text-slate-700',
  cancelado: 'bg-rose-100 text-rose-800',
};

const PRIORIDADE_COR = {
  baixa: 'text-slate-500',
  media: 'text-sky-700',
  alta: 'text-amber-700',
  critica: 'text-rose-700 font-semibold',
};

export function StatusBadge({ status }) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COR[status] || ''}`}>
      {STATUS_LABEL[status] || status}
    </span>
  );
}

export function Prioridade({ valor }) {
  return <span className={`text-sm capitalize ${PRIORIDADE_COR[valor] || ''}`}>{valor === 'media' ? 'média' : valor === 'critica' ? 'crítica' : valor}</span>;
}

export function Card({ children, className = '' }) {
  return <div className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>{children}</div>;
}

export function Botao({ children, variante = 'primario', className = '', ...props }) {
  const estilos = {
    primario: 'bg-indigo-600 text-white hover:bg-indigo-700 disabled:bg-indigo-300',
    secundario: 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50',
  };
  return (
    <button className={`rounded-lg px-4 py-2 text-sm font-medium transition ${estilos[variante]} ${className}`} {...props}>
      {children}
    </button>
  );
}

export function Erro({ mensagem }) {
  if (!mensagem) return null;
  return <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{mensagem}</p>;
}

export const dataHora = (iso) =>
  new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
