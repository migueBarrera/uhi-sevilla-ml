
import './App.css';
import { useNavigate } from 'react-router-dom';
import Footer from './Footer';


function App() {
  const navigate = useNavigate();
  return (
    <div className="app-wrapper">
      <main className="welcome-container">
        <h1>Predictor de isla de calor urbana Sevilla</h1>
        <p>
          Sevilla sufre temperaturas extremas agravadas por el efecto Isla de Calor Urbano (ICU), causado por la densa construcción, el asfalto y la falta de vegetación. Para combatir esto, el proyecto propone crear una herramienta predictiva e interactiva usando IA que permita a planificadores y ciudadanos evaluar el impacto real de medidas sostenibles (como la reforestación o el cambio de materiales) y cuantificar cuántos grados se reduciría la temperatura en el entorno.
        </p>
        <button
          onClick={() => navigate('/mapa')}
        >
          Entrar al simulador de islas de calor
        </button>
      </main>
      <Footer />
    </div>
  );
}

export default App;
