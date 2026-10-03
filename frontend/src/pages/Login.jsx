import { useState } from 'react';
import { Navigate, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Botao, Erro } from '../components/ui';

const DEMO = [
  ['admin@exemplo.com', 'Administrador'],
  ['gestor@exemplo.com', 'Gestor'],
  ['analista@exemplo.com', 'Analista'],
  ['solicitante@exemplo.com', 'Solicitante'],
];

export default function Login() {
  const { usuario, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [params] = useSearchParams();
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState('');
  const [carregando, setCarregando] = useState(false);

  if (usuario) return <Navigate to="/" replace />;

  const aviso = params.get('expirada')
    ? 'Sua sessão expirou. Entre novamente.'
    : params.get('inativo')
      ? 'Sessão encerrada por inatividade.'
      : '';

  async function entrar(e) {
    e.preventDefault();
    setErro('');
    setCarregando(true);
    try {
      await login(email, senha);
      navigate(location.state?.de || '/', { replace: true });
    } catch (err) {
      setErro(err.message);
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 to-indigo-900 p-4">
      <div className="w-full max-w-sm rounded-2xl bg-white p-8 shadow-xl">
        <h1 className="text-2xl font-bold text-slate-900">Entrar</h1>
        <p className="mt-1 text-sm text-slate-500">FastAPI + React RBAC Starter</p>

        {aviso && <p className="mt-4 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">{aviso}</p>}

        <form onSubmit={entrar} className="mt-6 space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">E-mail</span>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-indigo-500" />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Senha</span>
            <input type="password" required value={senha} onChange={(e) => setSenha(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-indigo-500" />
          </label>
          <Erro mensagem={erro} />
          <Botao type="submit" disabled={carregando} className="w-full">
            {carregando ? 'Entrando…' : 'Entrar'}
          </Botao>
        </form>

        <div className="mt-6 border-t border-slate-100 pt-4">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Contas de demonstração (senha demo12345)</p>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {DEMO.map(([e, perfil]) => (
              <button key={e} type="button" onClick={() => { setEmail(e); setSenha('demo12345'); }}
                className="rounded-lg border border-slate-200 px-2 py-1.5 text-xs text-slate-600 hover:bg-slate-50">
                {perfil}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
