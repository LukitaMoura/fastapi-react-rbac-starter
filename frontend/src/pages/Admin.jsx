import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { Botao, Card, Erro, dataHora } from '../components/ui';

export default function Admin() {
  const { usuario: eu } = useAuth();
  const [usuarios, setUsuarios] = useState([]);
  const [perfis, setPerfis] = useState([]);
  const [erro, setErro] = useState('');
  const [form, setForm] = useState({ nome: '', email: '', senha_inicial: '', perfil_ids: [] });

  const carregar = () =>
    Promise.all([api('/admin/usuarios'), api('/admin/perfis')])
      .then(([u, p]) => { setUsuarios(u); setPerfis(p); })
      .catch((e) => setErro(e.message));

  useEffect(() => { carregar(); }, []);

  async function atualizar(id, body) {
    setErro('');
    try {
      const novo = await api(`/admin/usuarios/${id}`, { method: 'PATCH', body });
      setUsuarios((us) => us.map((u) => (u.id === id ? novo : u)));
    } catch (e) {
      setErro(e.message);
    }
  }

  async function criar(e) {
    e.preventDefault();
    setErro('');
    try {
      await api('/admin/usuarios', { method: 'POST', body: form });
      setForm({ nome: '', email: '', senha_inicial: '', perfil_ids: [] });
      carregar();
    } catch (e) {
      setErro(e.message);
    }
  }

  const campo = 'rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500';

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Usuários e perfis</h1>
      <Erro mensagem={erro} />

      <Card>
        <h2 className="font-semibold text-slate-800">Novo usuário</h2>
        <form onSubmit={criar} className="mt-4 grid gap-3 md:grid-cols-4">
          <input required placeholder="Nome" value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} className={campo} />
          <input required type="email" placeholder="E-mail" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className={campo} />
          <input required minLength={8} type="password" placeholder="Senha inicial (8+)" value={form.senha_inicial}
            onChange={(e) => setForm({ ...form, senha_inicial: e.target.value })} className={campo} />
          <select value={form.perfil_ids[0] || ''} onChange={(e) => setForm({ ...form, perfil_ids: e.target.value ? [Number(e.target.value)] : [] })} className={campo}>
            <option value="">Perfil…</option>
            {perfis.map((p) => <option key={p.id} value={p.id}>{p.nome}</option>)}
          </select>
          <div className="md:col-span-4"><Botao type="submit">Criar usuário</Botao></div>
        </form>
      </Card>

      <Card className="overflow-x-auto p-0">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">Usuário</th>
              <th className="px-4 py-3">Perfis</th>
              <th className="px-4 py-3">Último acesso</th>
              <th className="px-4 py-3">Ativo</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {usuarios.map((u) => (
              <tr key={u.id}>
                <td className="px-4 py-3">
                  <p className="font-medium text-slate-800">{u.nome}</p>
                  <p className="text-xs text-slate-500">{u.email}</p>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1.5">
                    {perfis.map((p) => {
                      const tem = u.perfis.some((x) => x.id === p.id);
                      const ids = tem ? u.perfis.filter((x) => x.id !== p.id).map((x) => x.id) : [...u.perfis.map((x) => x.id), p.id];
                      return (
                        <button key={p.id} onClick={() => atualizar(u.id, { perfil_ids: ids })}
                          className={`rounded-full px-2.5 py-0.5 text-xs ${tem ? 'bg-indigo-600 text-white' : 'border border-slate-300 text-slate-500 hover:bg-slate-50'}`}>
                          {p.nome}
                        </button>
                      );
                    })}
                  </div>
                </td>
                <td className="px-4 py-3 text-slate-500">{u.ultimo_acesso ? dataHora(u.ultimo_acesso) : '—'}</td>
                <td className="px-4 py-3">
                  <input type="checkbox" checked={u.ativo} disabled={u.id === eu.id}
                    onChange={(e) => atualizar(u.id, { ativo: e.target.checked })} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <Card>
        <h2 className="font-semibold text-slate-800">Permissões por perfil</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {perfis.map((p) => (
            <div key={p.id} className="rounded-lg border border-slate-200 p-4">
              <p className="font-medium text-slate-800">{p.nome}</p>
              <p className="text-xs text-slate-500">{p.descricao}</p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {p.permissoes.map((perm) => (
                  <code key={perm.id} className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-700">{perm.chave}</code>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
