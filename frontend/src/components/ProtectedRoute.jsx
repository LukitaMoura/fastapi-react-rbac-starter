import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({ permissao, children }) {
  const { usuario, pode } = useAuth();
  const location = useLocation();

  if (!usuario) return <Navigate to="/login" replace state={{ de: location.pathname }} />;
  if (permissao && !pode(permissao)) {
    return (
      <div className="p-10 text-center text-slate-500">
        <p className="text-lg font-semibold text-slate-700">Acesso negado</p>
        <p className="mt-1 text-sm">Esta página exige a permissão <code>{permissao}</code>.</p>
      </div>
    );
  }
  return children;
}
