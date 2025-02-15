import React, { useState, useEffect, useRef } from "react";
import { Slider, Space, Card, Button } from "antd";

interface Generation {
  text: string;
  color: string;
}

interface Params {
  temperature: number;
  top_p: number;
  top_k: number;
  num_predict: number;
}

// Custom hook to manage streaming generations.
function useStreamingGenerations() {
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [currentText, setCurrentText] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const currentTextRef = useRef(currentText);

  // Update the ref whenever currentText changes.
  useEffect(() => {
    currentTextRef.current = currentText;
  }, [currentText]);

  const colors = ["#FF5733", "#33FF57", "#3357FF", "#F833FF", "#33FFF8"];

  const connect = () => {
    if (eventSourceRef.current) return; // Already connected.
    const eventSource = new EventSource("http://localhost:8000/stream");
    eventSourceRef.current = eventSource;
    setIsConnected(true);

    eventSource.onmessage = (event) => {
      currentTextRef.current += event.data;
      setCurrentText(currentTextRef.current);
    };

    eventSource.addEventListener("done", () => {
      setGenerations((prev) => {
        const newGeneration: Generation = {
          text: currentTextRef.current,
          color: colors[prev.length % colors.length],
        };
        return [...prev, newGeneration];
      });
      eventSource.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    });
  };

  return { generations, currentText, connect, setCurrentText, isConnected };
}

const LlamaStream = () => {
  const { generations, currentText, connect, setCurrentText, isConnected } = useStreamingGenerations();
  const [params, setParams] = useState<Params>({
    temperature: 0.8,
    top_p: 0.95,
    top_k: 50,
    num_predict: 64,
  });

  // Reset current text and trigger connection.
  const handleGenerate = () => {
    setCurrentText("");
    connect();
  };

  const updateParameter = (paramName: keyof Params, value: number) => {
    setParams((prev) => ({
      ...prev,
      [paramName]: value,
    }));
  };

  return (
    <Space direction="vertical" style={{ width: "100%" }}>
      <Card title="Current Response">
        <div>{currentText}</div>
        <Button onClick={handleGenerate} disabled={isConnected}>
          New Generation
        </Button>
      </Card>
      <Card title="Past Responses">
        {generations.map((gen, idx) => (
          <Card key={idx} style={{ borderLeft: `4px solid ${gen.color}` }}>
            {gen.text}
          </Card>
        ))}
      </Card>
      <Card title="Parameters">
        <Space direction="vertical">
          <div>
            <span>Temperature: </span>
            <Slider
              min={0}
              max={1}
              step={0.01}
              value={params.temperature}
              onChange={(value: number) => updateParameter("temperature", value)}
            />
          </div>
          <div>
            <span>Top_p: </span>
            <Slider
              min={0}
              max={1}
              step={0.01}
              value={params.top_p}
              onChange={(value: number) => updateParameter("top_p", value)}
            />
          </div>
          <div>
            <span>Top_k: </span>
            <Slider
              min={0}
              max={100}
              step={1}
              value={params.top_k}
              onChange={(value: number) => updateParameter("top_k", value)}
            />
          </div>
          <div>
            <span>num_predict: </span>
            <Slider
              min={4}
              max={128}
              step={4}
              value={params.num_predict}
              onChange={(value: number) => updateParameter("num_predict", value)}
            />
          </div>
        </Space>
      </Card>
    </Space>
  );
};

export default LlamaStream; 