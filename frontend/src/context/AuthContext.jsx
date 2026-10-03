import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { api, sessao } from '../lib/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(() => (sessao.token() ? sessao.usuario() : null));

  const login = useCallback(async (email, senha) => {
    const data = await api('/auth/login', { method: 'POST', body: { email, senha } });
    sessao.salvar(data.access_token, data.usuario);
    setUsuario(data.usuario);
    return data.usuario;
  }, []);

  const logout = useCallback(() => {
    sessao.limpar();
    setUsuario(null);
  }, []);

  // O gate da UI usa a MESMA chave que o endpoint exige no backend:
  // se divergirem, o usuário vê um botão e leva 403 ao clicar.
  const pode = useCallback((chave) => !!usuario?.permissoes?.includes(chave), [usuario]);

  const value = useMemo(() => ({ usuario, login, logout, pode }), [usuario, login, logout, pode]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
