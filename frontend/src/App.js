import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { WeatherProvider } from './context/WeatherContext';
import Dashboard from './pages/Dashboard';
import './App.css';

function App() {
  return (
    <WeatherProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </div>
      </Router>
    </WeatherProvider>
  );
}

export default App;
