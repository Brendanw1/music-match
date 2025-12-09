import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QuizIntro, QuizContainer } from './components/Quiz';
import { ResultsContainer } from './components/Results';
import { ClusterExplorer } from './components/Recommendations';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
        <Routes>
          <Route path="/" element={<QuizIntro />} />
          <Route path="/quiz" element={<QuizContainer />} />
          <Route path="/results" element={<ResultsContainer />} />
          <Route path="/explore" element={<ClusterExplorer />} />
          <Route path="/recommendations/:clusterId" element={<ClusterExplorer />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
