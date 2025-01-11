import React, { useState, useEffect } from 'react';
import { Slider, Space, Card } from 'antd';
import styles from './LlamaStream.module.css';

interface Params {
    temperature: number;
    top_p: number;
    top_k: number;
    num_ctx: number;
    num_predict: number;
}

const LlamaStream: React.FC = () => {
    const [streamText, setStreamText] = useState<string>('');
    const [params, setParams] = useState<Params>({
        temperature: 0.4,
        top_p: 0.4,
        top_k: 30,
        num_ctx: 1024,
        num_predict: 48
    });

    useEffect(() => {
        const eventSource = new EventSource('http://localhost:8000/stream');
        
        eventSource.onmessage = (event) => {
            setStreamText(prev => prev + event.data);
            // Optional: Auto-scroll to bottom
            // document.getElementById('stream-box')?.scrollTo(0, document.getElementById('stream-box')?.scrollHeight);
        };

        return () => {
            eventSource.close();
        };
    }, []);

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

    return (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Card className={styles.streamBox} id="stream-box">
                {streamText}
            </Card>
            
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
                        <label>Context Window</label>
                        <Slider
                            value={params.num_ctx}
                            min={128}
                            max={4096}
                            step={128}
                            onChange={(value: number) => updateParameter('num_ctx', value)}
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