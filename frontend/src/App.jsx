import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import InternalLayout from './layouts/InternalLayout';
import Login from './pages/Login';
import Inicio from './pages/Inicio';
import Chamados from './pages/Chamados';
import ChamadoDetalhe from './pages/ChamadoDetalhe';
import Admin from './pages/Admin';
import Auditoria from './pages/Auditoria';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedRoute><InternalLayout /></ProtectedRoute>}>
            <Route index element={<Inicio />} />
            <Route path="chamados" element={<Chamados />} />
            <Route path="chamados/:id" element={<ChamadoDetalhe />} />
            {/* mesma chave de permissão que o endpoint exige no backend */}
            <Route path="admin" element={<ProtectedRoute permissao="admin.gerenciar"><Admin /></ProtectedRoute>} />
            <Route path="auditoria" element={<ProtectedRoute permissao="auditoria.ver"><Auditoria /></ProtectedRoute>} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
