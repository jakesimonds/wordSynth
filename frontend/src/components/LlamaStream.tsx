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
// NOTE: We pass the current params so that the stream connection
// uses up‑to‑date values (including num_predict) when connecting.
function useStreamingGenerations(params: Params) {
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [currentText, setCurrentText] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const currentTextRef = useRef(currentText);

  // Keep the ref updated with the latest currentText
  useEffect(() => {
    currentTextRef.current = currentText;
  }, [currentText]);

  const colors = ["#FF5733", "#33FF57", "#3357FF", "#F833FF", "#33FFF8"];

  // handleGenerate resets current text and connects to the stream,
  // including the current parameter values in the query string.
  const handleGenerate = () => {
    // Reset the current text
    currentTextRef.current = "";
    setCurrentText("");

    // Prevent duplicate connections
    if (eventSourceRef.current) return;

    // Build a query string based on the current parameter values
    const queryParams = new URLSearchParams({
      temperature: params.temperature.toString(),
      top_p: params.top_p.toString(),
      top_k: params.top_k.toString(),
      num_predict: params.num_predict.toString(),
    });

    // Open a connection to the stream endpoint with the query parameters.
    const eventSource = new EventSource(
      `http://localhost:8000/stream?${queryParams.toString()}`
    );
    eventSourceRef.current = eventSource;
    setIsConnected(true);

    eventSource.onmessage = (event) => {
      currentTextRef.current += event.data;
      setCurrentText(currentTextRef.current);
    };

    eventSource.addEventListener("done", () => {
      // Save the completed generation in past responses.
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

  return { generations, currentText, isConnected, handleGenerate };
}

const LlamaStream = () => {
  const [params, setParams] = useState<Params>({
    temperature: 0.7,
    top_p: 0.9,
    top_k: 40,
    num_predict: 4,
  });

  // Update parameters when sliders move.
  const updateParameter = (paramName: keyof Params, value: number) => {
    setParams((prev) => ({
      ...prev,
      [paramName]: value,
    }));
  };

  // Pass the current parameters to the custom hook.
  const { generations, currentText, isConnected, handleGenerate } =
    useStreamingGenerations(params);

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
              onChange={(value: number) =>
                updateParameter("num_predict", value)
              }
            />
          </div>
        </Space>
      </Card>
    </Space>
  );
};

export default LlamaStream; 