export const API_BASE = import.meta.env.VITE_API_BASE || '/api';

const TOKEN_KEY = 'starter_token';
const USER_KEY = 'starter_usuario';

// sessionStorage (e não localStorage): fechar a aba encerra a sessão.
// Em máquina compartilhada, o próximo usuário não herda a sessão do anterior.
export const sessao = {
  token: () => sessionStorage.getItem(TOKEN_KEY),
  usuario: () => {
    try {
      return JSON.parse(sessionStorage.getItem(USER_KEY));
    } catch {
      return null;
    }
  },
  salvar: (token, usuario) => {
    sessionStorage.setItem(TOKEN_KEY, token);
    sessionStorage.setItem(USER_KEY, JSON.stringify(usuario));
  },
  limpar: () => {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
  },
};

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

/** fetch autenticado: injeta o Bearer, converte JSON e trata sessão expirada (401). */
export async function api(path, { method = 'GET', body, params } = {}) {
  const url = new URL(`${API_BASE}${path}`, window.location.origin);
  Object.entries(params || {}).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v);
  });

  const headers = {};
  const token = sessao.token();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers['Content-Type'] = 'application/json';

  const res = await fetch(url, { method, headers, body: body !== undefined ? JSON.stringify(body) : undefined });

  if (res.status === 401 && token) {
    sessao.limpar();
    window.location.href = '/login?expirada=1';
    throw new ApiError(401, 'Sessão expirada.');
  }
  if (res.status === 204) return null;

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = Array.isArray(data.detail) ? data.detail.map((d) => d.msg).join('; ') : data.detail;
    throw new ApiError(res.status, detail || `Erro ${res.status}`);
  }
  return data;
}
