import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { Card, Erro, STATUS_LABEL } from '../components/ui';

export default function Inicio() {
  const { usuario, pode } = useAuth();
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState('');

  useEffect(() => {
    api('/chamados/dashboard').then(setDados).catch((e) => setErro(e.message));
  }, []);

  const total = dados ? Object.values(dados.por_status).reduce((a, b) => a + b, 0) : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Olá, {usuario.nome.split(' ')[0]}</h1>
        <p className="text-sm text-slate-500">
          {pode('chamados.ver_todos') ? 'Visão de todos os chamados.' : 'Visão dos seus chamados.'}
        </p>
      </div>
      <Erro mensagem={erro} />

      {dados && (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
            {Object.entries(dados.por_status).map(([status, n]) => (
              <Link key={status} to={`/chamados?status=${status}`}>
                <Card className="transition hover:border-indigo-300">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{STATUS_LABEL[status]}</p>
                  <p className="mt-2 text-3xl font-bold text-slate-900">{n}</p>
                </Card>
              </Link>
            ))}
          </div>

          {dados.abertos_ha_mais_de_7_dias > 0 && (
            <Card className="flex items-center gap-3 border-amber-200 bg-amber-50">
              <AlertTriangle className="text-amber-600" size={20} />
              <p className="text-sm text-amber-900">
                <strong>{dados.abertos_ha_mais_de_7_dias}</strong> chamado(s) em aberto há mais de 7 dias.
              </p>
            </Card>
          )}

          <Card>
            <h2 className="font-semibold text-slate-800">Distribuição por status</h2>
            <div className="mt-4 space-y-2">
              {Object.entries(dados.por_status).map(([status, n]) => (
                <div key={status} className="flex items-center gap-3 text-sm">
                  <span className="w-28 text-slate-600">{STATUS_LABEL[status]}</span>
                  <div className="h-3 flex-1 rounded-full bg-slate-100">
                    <div className="h-3 rounded-full bg-indigo-500" style={{ width: total ? `${(n / total) * 100}%` : 0 }} />
                  </div>
                  <span className="w-8 text-right tabular-nums text-slate-700">{n}</span>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
