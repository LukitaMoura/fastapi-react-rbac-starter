import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { ClipboardList, History, LayoutDashboard, LogOut, Menu, Users, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useIdleLogout } from '../hooks/useIdleLogout';

// Cada item declara a permissão que exige: o menu só mostra o que o usuário pode usar
const MENU = [
  { to: '/', label: 'Início', icon: LayoutDashboard },
  { to: '/chamados', label: 'Chamados', icon: ClipboardList },
  { to: '/admin', label: 'Usuários e perfis', icon: Users, permissao: 'admin.gerenciar' },
  { to: '/auditoria', label: 'Auditoria', icon: History, permissao: 'auditoria.ver' },
];

export default function InternalLayout() {
  const { usuario, logout, pode } = useAuth();
  const navigate = useNavigate();
  const [aberto, setAberto] = useState(false);

  const sair = () => {
    logout();
    navigate('/login');
  };
  useIdleLogout(() => {
    logout();
    navigate('/login?inativo=1');
  }, 30);

  const itens = MENU.filter((i) => !i.permissao || pode(i.permissao));

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside
        className={`fixed inset-y-0 left-0 z-30 w-64 transform bg-slate-900 text-slate-200 transition md:static md:translate-x-0 ${
          aberto ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-16 items-center justify-between px-5">
          <span className="text-lg font-semibold text-white">RBAC Starter</span>
          <button className="md:hidden" onClick={() => setAberto(false)} aria-label="Fechar menu">
            <X size={20} />
          </button>
        </div>
        <nav className="space-y-1 px-3">
          {itens.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setAberto(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm ${
                  isActive ? 'bg-indigo-600 text-white' : 'hover:bg-slate-800'
                }`
              }
            >
              <Icon size={18} /> {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 md:px-8">
          <button className="md:hidden" onClick={() => setAberto(true)} aria-label="Abrir menu">
            <Menu size={22} />
          </button>
          <div className="ml-auto flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-slate-800">{usuario.nome}</p>
              <p className="text-xs text-slate-500">{usuario.perfis.map((p) => p.nome).join(', ')}</p>
            </div>
            <button onClick={sair} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100" aria-label="Sair">
              <LogOut size={18} />
            </button>
          </div>
        </header>
        <main className="flex-1 p-4 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
