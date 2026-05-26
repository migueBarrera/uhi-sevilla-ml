import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import MapView from './MapView';

export default function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/mapa" element={<MapView />} />
      </Routes>
    </BrowserRouter>
  );
}
