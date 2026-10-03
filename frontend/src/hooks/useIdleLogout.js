import { useEffect, useRef } from 'react';

const EVENTOS = ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart'];

/** Encerra a sessão após `minutos` sem interação (estação destravada não fica logada). */
export function useIdleLogout(onIdle, minutos = 30) {
  const timer = useRef();
  const callback = useRef(onIdle);
  callback.current = onIdle;

  useEffect(() => {
    const reiniciar = () => {
      clearTimeout(timer.current);
      timer.current = setTimeout(() => callback.current(), minutos * 60 * 1000);
    };
    EVENTOS.forEach((e) => window.addEventListener(e, reiniciar, { passive: true }));
    reiniciar();
    return () => {
      clearTimeout(timer.current);
      EVENTOS.forEach((e) => window.removeEventListener(e, reiniciar));
    };
  }, [minutos]);
}
