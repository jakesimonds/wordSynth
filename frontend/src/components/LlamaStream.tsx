import React, { useState } from 'react';
import { Slider, Space, Card } from 'antd';

interface Params {
    temperature: number;
    top_p: number;
    top_k: number;
    num_predict: number;
}

// Custom hook to manage streaming
function useStreamingText() {
    const [text, setText] = useState('');
    const [isConnected, setIsConnected] = useState(false);

    const connect = () => {
        const eventSource = new EventSource('http://localhost:8000/stream');
        setIsConnected(true);

        eventSource.onmessage = (event) => {
            setText(prev => prev + event.data);
        };

        eventSource.addEventListener('done', () => {
            setText('');
            eventSource.close();
            connect(); // Reconnect for next generation
        });

        return () => {
            eventSource.close();
            setIsConnected(false);
        };
    };

    // Initial connection
    if (!isConnected) {
        connect();
    }

    return text;
}

const LlamaStream: React.FC = () => {
    const currentResponse = useStreamingText();
    const [params, setParams] = useState<Params>({
        temperature: 0.4,
        top_p: 0.4,
        top_k: 30,
        num_predict: 48
    });

    const updateParameter = async (key: keyof Params, value: number) => {
        const newParams = { ...params, [key]: value };
        setParams(newParams);
        
        try {
            await fetch('http://localhost:8000/update-params', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ [key]: value }),
            });
        } catch (error) {
            console.error('Failed to update parameters:', error);
        }
    };

    const injectTokens = async (text: string) => {
        try {
            await fetch('http://localhost:8000/inject-tokens', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text }),
            });
        } catch (error) {
            console.error('Failed to inject tokens:', error);
        }
    };

    return (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Card 
                title="Current Response"
                style={{ minHeight: '400px' }}
            >
                <div>
                    {currentResponse || 'Waiting for response...'}
                </div>
            </Card>
            
            <button 
                onClick={() => injectTokens("but wait, let's reconsider")}
                style={{ marginBottom: '10px' }}
            >
                Inject Reconsideration
            </button>
            
            <Card title="Parameters">
                <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                        <label>Temperature</label>
                        <Slider
                            value={params.temperature}
                            min={0}
                            max={2}
                            step={0.1}
                            onChange={(value: number) => updateParameter('temperature', value)}
                        />
                    </div>
                    <div>
                        <label>Top P</label>
                        <Slider
                            value={params.top_p}
                            min={0}
                            max={1}
                            step={0.1}
                            onChange={(value: number) => updateParameter('top_p', value)}
                        />
                    </div>
                    <div>
                        <label>Top K</label>
                        <Slider
                            value={params.top_k}
                            min={1}
                            max={100}
                            step={5}
                            onChange={(value: number) => updateParameter('top_k', value)}
                        />
                    </div>
                    <div>
                        <label>Prediction Length</label>
                        <Slider
                            value={params.num_predict}
                            min={4}
                            max={128}
                            step={4}
                            onChange={(value: number) => updateParameter('num_predict', value)}
                        />
                    </div>
                </Space>
            </Card>
        </Space>
    );
};

export default LlamaStream; 