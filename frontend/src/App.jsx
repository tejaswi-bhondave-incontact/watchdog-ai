import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Overview from './pages/Overview';
import Monitors from './pages/Monitors';
import BlindSpots from './pages/BlindSpots';
import GeneratedTests from './pages/GeneratedTests';
import TestResults from './pages/TestResults';
import JiraInput from './pages/JiraInput';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/monitors" element={<Monitors />} />
            <Route path="/blindspots" element={<BlindSpots />} />
            <Route path="/tests" element={<GeneratedTests />} />
            <Route path="/results" element={<TestResults />} />
            <Route path="/jira" element={<JiraInput />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
