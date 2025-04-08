import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import LlamaStream from './components/LlamaStream';

import 'antd/dist/reset.css';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/app" element={<LlamaStream />} />
      </Routes>
    </Router>
  );
};

export default App;
