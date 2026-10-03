import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { Card, Erro, dataHora } from '../components/ui';

export default function Auditoria() {
  const [linhas, setLinhas] = useState([]);
  const [erro, setErro] = useState('');

  useEffect(() => {
    api('/admin/auditoria', { params: { limite: 200 } }).then(setLinhas).catch((e) => setErro(e.message));
  }, []);

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold text-slate-900">Trilha de auditoria</h1>
      <Erro mensagem={erro} />
      <Card className="overflow-x-auto p-0">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">Quando</th>
              <th className="px-4 py-3">Quem</th>
              <th className="px-4 py-3">Ação</th>
              <th className="px-4 py-3">Registro</th>
              <th className="px-4 py-3">Detalhe</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {linhas.map((l) => (
              <tr key={l.id}>
                <td className="whitespace-nowrap px-4 py-2.5 text-slate-500">{dataHora(l.criado_em)}</td>
                <td className="px-4 py-2.5">{l.usuario?.nome || '—'}</td>
                <td className="px-4 py-2.5"><code className="text-xs">{l.acao}</code></td>
                <td className="px-4 py-2.5 text-slate-600">{l.entidade}{l.entidade_id ? ` #${l.entidade_id}` : ''}</td>
                <td className="px-4 py-2.5 text-slate-600">{l.detalhe}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
