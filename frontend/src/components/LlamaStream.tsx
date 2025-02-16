import React, { useState, useEffect, useRef } from "react";
import { Slider, Space, Card, Skeleton } from "antd";


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

  // Auto-generation: whenever we're not connected (and thus generation has finished),
  // wait for a global delay (500ms by default) and trigger handleGenerate.
  useEffect(() => {
    const pollInterval = 500; // Delay in milliseconds.
    if (!isConnected) {
      const timer = setTimeout(() => {
        handleGenerate();
      }, pollInterval);
      return () => clearTimeout(timer);
    }
  }, [isConnected, handleGenerate]);

  return (
    <div
      style={{
        display: "flex",
        width: "100%",
        gap: "16px",
        alignItems: "flex-start",
      }}
    >
      {/* Left column for Parameters */}
      <div style={{ flex: "0 0 300px" }}>
        <Card title="Parameters">
          <Space direction="vertical">
            <div>
              <span>Temperature: </span>
              <Slider
                min={0}
                max={1}
                step={0.01}
                value={params.temperature}
                onChange={(value: number) =>
                  updateParameter("temperature", value)
                }
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
      </div>

      {/* Right column for Generations */}
      <div style={{ flex: "1" }}>
        <Card title="Current Response" style={{ minHeight: "120px" }}>
          <div>{currentText}</div>
        </Card>
        <Card title="Past Responses">
          {(() => {
            const maxSlots = 10;
            // Show the 10 most recent responses if there are more than 10.
            const displayed =
              generations.length > maxSlots
                ? generations.slice(-maxSlots)
                : generations;
            const fillerCount = maxSlots - displayed.length;
            return (
              <>
                {displayed.map((gen, idx) => (
                  <Card
                    key={`real-${idx}`}
                    style={{
                      borderLeft: `4px solid ${gen.color}`,
                      marginBottom: 8,
                    }}
                  >
                    {gen.text}
                  </Card>
                ))}
                {Array.from({ length: fillerCount }).map((_, idx) => (
                  <Card key={`filler-${idx}`} style={{ marginBottom: 8 }}>
                    <Skeleton active paragraph={{ rows: 2 }} />
                  </Card>
                ))}
              </>
            );
          })()}
        </Card>
      </div>
    </div>
  );
};

export default LlamaStream; 