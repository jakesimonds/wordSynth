import { useState, useEffect, useRef } from "react";
import { Slider, Space, Card, Skeleton, Select, Button } from "antd";

//test test 
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
function useStreamingGenerations(params: Params, isPaused: boolean) {
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

  // Modify the auto-generation effect
  useEffect(() => {
    const pollInterval = 500;
    if (!isConnected && !isPaused) {
      const timer = setTimeout(() => {
        handleGenerate();
      }, pollInterval);
      return () => clearTimeout(timer);
    }
  }, [isConnected, isPaused, handleGenerate]);

  return { generations, currentText, isConnected, handleGenerate };
}

const LlamaStream = () => {
  const [params, setParams] = useState<Params>({
    temperature: 0.7,
    top_p: 0.9,
    top_k: 40,
    num_predict: 4,
  });
  const [isPaused, setIsPaused] = useState(false);
  const [contexts, setContexts] = useState<string[]>([]);
  const [currentContext, setCurrentContext] = useState<string>("");

  // Add this function
  const togglePause = async () => {
    try {
      const response = await fetch('http://localhost:8000/toggle-pause');
      const data = await response.json();
      setIsPaused(data.is_paused);
    } catch (error) {
      console.error('Failed to toggle pause state:', error);
    }
  };

  // Update parameters when sliders move.
  const updateParameter = (paramName: keyof Params, value: number) => {
    setParams((prev) => ({
      ...prev,
      [paramName]: value,
    }));
  };

  // Add this effect to fetch contexts when component mounts
  useEffect(() => {
    fetch('http://localhost:8000/contexts')
      .then(res => res.json())
      .then(data => {
        setContexts(data.contexts);
        setCurrentContext(data.current);
      });
  }, []);

  // Add this function to handle context changes
  const handleContextChange = async (index: number) => {
    const response = await fetch(`http://localhost:8000/set-context?context_index=${index}`, {
      method: 'POST'
    });
    if (response.ok) {
      const data = await response.json();
      setCurrentContext(data.current);
    }
  };

  const { generations, currentText } = useStreamingGenerations(params, isPaused);


  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* Add this style tag for hover effects */}
      <style>
        {`
          .header-link {
            color: #b19dd8;
            text-decoration: none;
            transition: color 0.2s;
          }
          .header-link:hover {
            color: #e100ff;
          }
        `}
      </style>

      {/* Header Section */}
      <div style={{
        width: "100%",
        padding: "1rem",
        background: "linear-gradient(45deg, #2b1331, #000000)",
        marginBottom: "1rem",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "0.5rem"
      }}>
        {/* Title */}
        <h1 style={{
          margin: 0,
          fontSize: "3.5rem",
          fontFamily: "'Press Start 2P', system-ui",
          background: "linear-gradient(45deg, #e100ff, #7700ff)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          textShadow: "0 0 20px rgba(231,0,255,0.5)",
          letterSpacing: "0.2em",
          textAlign: "center"
        }}>
          WORD SYNTH
        </h1>
        
        {/* Updated links */}
        <div style={{
          display: "flex",
          gap: "2rem",
          fontSize: "0.9rem"
        }}>
          <a 
            href="https://github.com/jakesimonds/wordSynth" 
            target="_blank" 
            rel="noopener noreferrer"
            className="header-link"
          >
            github
          </a>
          <a 
            href="https://jakesimonds.github.io/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="header-link"
          >
            jakesimonds
          </a>
        </div>
      </div>

      {/* Your existing main content div */}
      <div style={{
        display: "flex",
        width: "100%",
        flex: 1,
        padding: "1rem",
        gap: "16px",
      }}>
        {/* Left column for Parameters - fixed width */}
        <div style={{ 
          flex: "0 0 300px"
        }}>
          <Space direction="vertical" style={{ width: '100%', gap: '16px' }}>
            <Card title="Current Prompt">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Select
                  value={contexts.indexOf(currentContext)}
                  onChange={handleContextChange}
                  style={{ width: '250px' }}
                >
                  {contexts.map((context, index) => (
                    <Select.Option 
                      key={index} 
                      value={index}
                      title={context}
                    >
                      {context.length > 30 ? context.slice(0, 30) + '...' : context}
                    </Select.Option>
                  ))}
                </Select>
                <div style={{ 
                  marginTop: '8px',
                  padding: '8px',
                  background: '#f5f5f5',
                  borderRadius: '4px',
                  fontSize: '0.9em',
                  wordWrap: 'break-word',
                  whiteSpace: 'pre-wrap',
                  width: '100%',
                  maxWidth: '300px',
                  overflowWrap: 'break-word'
                }}>
                  {currentContext}
                </div>
              </Space>
            </Card>

            <Card title="Parameters">
              <Space direction="vertical" style={{ width: '100%', display: 'flex', alignItems: 'center' }}>

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
                    min={1}
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
                <button
                  onClick={togglePause}
                  style={{
                    width: "100%",
                    padding: "12px",
                    marginBottom: "26px",
                    fontSize: "28px",
                    backgroundColor: isPaused ? "#4CAF50" : "#f44336",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer"
                  }}
                >
                  {isPaused ? "Resume" : "Pause"}
                </button>

              </Space>
            </Card>
          </Space>
        </div>

        {/* Right column for Responses - takes remaining width */}
        <div style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          gap: "16px",
          height: "100%", // Full height of parent
          minHeight: 0, // Important for Firefox
        }}>
          {/* Current Response - fixed height */}
          <Card 
            title="Current Response" 
            style={{ 
              height: "120px",
              overflow: "auto"
            }}
          >
            <div>{currentText}</div>
          </Card>

          {/* Past Responses - takes remaining height, scrolls */}
          <Card 
            title="Past Responses"
            style={{
              flex: 1,
              overflow: "auto",
              minHeight: 0
            }}
          >
            <div style={{
              display: "flex",
              flexDirection: "column",
              gap: "8px"
            }}>
              {(() => {
                const maxSlots = 5;
                const displayed = [...(generations.length > maxSlots
                  ? generations.slice(-maxSlots)
                  : generations)].reverse();
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
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default LlamaStream; 