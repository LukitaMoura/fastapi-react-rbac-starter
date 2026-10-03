import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { Botao, Card, Erro, Prioridade, STATUS_LABEL, StatusBadge, dataHora } from '../components/ui';

export default function ChamadoDetalhe() {
  const { id } = useParams();
  const { pode } = useAuth();
  const [chamado, setChamado] = useState(null);
  const [erro, setErro] = useState('');
  const [comentario, setComentario] = useState('');
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    api(`/chamados/${id}`).then(setChamado).catch((e) => setErro(e.message));
  }, [id]);

  async function mudarStatus(status) {
    setErro('');
    setEnviando(true);
    try {
      setChamado(await api(`/chamados/${id}/transicao`, { method: 'POST', body: { status, comentario } }));
      setComentario('');
    } catch (e) {
      setErro(e.message);
    } finally {
      setEnviando(false);
    }
  }

  if (!chamado) return erro ? <Erro mensagem={erro} /> : <p className="text-slate-400">Carregando…</p>;

  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <Link to="/chamados" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-800">
        <ArrowLeft size={16} /> Voltar
      </Link>

      <Card>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs text-slate-500">Chamado #{chamado.id} · {chamado.categoria}</p>
            <h1 className="mt-1 text-xl font-bold text-slate-900">{chamado.titulo}</h1>
          </div>
          <StatusBadge status={chamado.status} />
        </div>
        {chamado.descricao && <p className="mt-4 whitespace-pre-line text-sm text-slate-700">{chamado.descricao}</p>}
        <dl className="mt-5 grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
          <div><dt className="text-slate-500">Prioridade</dt><dd><Prioridade valor={chamado.prioridade} /></dd></div>
          <div><dt className="text-slate-500">Solicitante</dt><dd>{chamado.solicitante.nome}</dd></div>
          <div><dt className="text-slate-500">Responsável</dt><dd>{chamado.responsavel?.nome || '—'}</dd></div>
          <div><dt className="text-slate-500">Atualizado</dt><dd>{dataHora(chamado.atualizado_em)}</dd></div>
        </dl>
      </Card>

      {pode('chamados.tratar') && chamado.transicoes_possiveis.length > 0 && (
        <Card className="space-y-3">
          <h2 className="font-semibold text-slate-800">Tratar chamado</h2>
          <textarea rows={2} value={comentario} onChange={(e) => setComentario(e.target.value)}
            placeholder="Comentário (obrigatório para 'Aguardando')"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500" />
          <div className="flex flex-wrap gap-2">
            {chamado.transicoes_possiveis.map((s) => (
              <Botao key={s} disabled={enviando} variante={s === 'cancelado' ? 'secundario' : 'primario'} onClick={() => mudarStatus(s)}>
                {STATUS_LABEL[s]}
              </Botao>
            ))}
          </div>
          <Erro mensagem={erro} />
        </Card>
      )}

      <Card>
        <h2 className="font-semibold text-slate-800">Histórico</h2>
        <ol className="mt-4 space-y-4 border-l-2 border-slate-200 pl-5">
          {chamado.historico.map((h, i) => (
            <li key={i} className="relative">
              <span className="absolute -left-[27px] top-1 h-3 w-3 rounded-full bg-indigo-500" />
              <p className="text-sm text-slate-800">
                {h.status_de ? <>{STATUS_LABEL[h.status_de]} → </> : null}<strong>{STATUS_LABEL[h.status_para]}</strong>
              </p>
              {h.comentario && <p className="text-sm text-slate-600">{h.comentario}</p>}
              <p className="text-xs text-slate-400">{h.usuario.nome} · {dataHora(h.criado_em)}</p>
            </li>
          ))}
        </ol>
      </Card>
    </div>
  );
}
