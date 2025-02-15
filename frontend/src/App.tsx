import LlamaStream from './components/LlamaStream';
import { StreamProvider } from './contexts/StreamContext';
import 'antd/dist/reset.css';

function App() {
  return (
    <div style={{ 
      padding: '20px', 
      width: '100vw',  // Full viewport width
      minHeight: '100vh',  // Full viewport height
      boxSizing: 'border-box'  // Include padding in width calculation
    }}>
      <StreamProvider>
        <LlamaStream />
      </StreamProvider>
    </div>
  );
}

export default App;
