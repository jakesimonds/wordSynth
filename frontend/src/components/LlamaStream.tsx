import { useState, useEffect, useRef } from "react";
import { Slider, Space, Card, Skeleton, Select } from "antd";
import { useLocation, Navigate } from 'react-router-dom';

// Define API_BASE to handle both development and production environments
const API_BASE = import.meta.env.DEV 
  ? 'http://localhost:8000' 
  : '/api';

//test test 
interface Generation {
  text: string;
  color: string;
  params: {
    temperature: number;
    top_p: number;
    top_k: number;
    num_predict: number;
    repeat_penalty: number;
    presence_penalty: number;
    frequency_penalty: number;
    mirostat_mode: number;
    mirostat_tau: number;
    mirostat_eta: number;
  };
  tokens?: GeneratedToken[];  // Changed from TokenData[] to GeneratedToken[]
}

interface Params {
  temperature: number;
  top_p: number;
  top_k: number;
  num_predict: number;
  repeat_penalty: number;
  presence_penalty: number;
  frequency_penalty: number;
  mirostat_mode: number;  // 0 = disabled, 1 = Mirostat, 2 = Mirostat 2.0
  mirostat_tau: number;   // Target entropy
  mirostat_eta: number;   // Learning rate
}

// In LlamaStream.tsx add interface for voice parameters
interface VoiceParams {
  pitch: number;
  speed: number;
  tempo: number; // artificial pause between chunks in seconds
}

// First, add interfaces for token data
interface TokenData {
  text: string;
  id: number;
  prob: number;
  top5: {
    text: string;
    id: number;
    prob: number;
  }[];
}

interface GeneratedToken {
  text: string;
  data: TokenData;
}

// Custom hook to manage streaming generations.
// NOTE: We pass the current params so that the stream connection
// uses up‑to‑date values (including num_predict) when connecting.
function useStreamingGenerations(params: Params, isPaused: boolean, currentContext: string, voiceParams: VoiceParams) {
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [currentText, setCurrentText] = useState("");
  const [currentTokens, setCurrentTokens] = useState<GeneratedToken[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const currentTextRef = useRef(currentText);
  const currentTokensRef = useRef<GeneratedToken[]>([]);

  // Keep the refs updated with the latest values
  useEffect(() => {
    currentTextRef.current = currentText;
  }, [currentText]);

  useEffect(() => {
    currentTokensRef.current = currentTokens;
  }, [currentTokens]);

  const colors = ["#FF5733", "#33FF57", "#3357FF", "#F833FF", "#33FFF8"];

  // Update the speakText function to use voice parameters
  const speakText = (text: string) => {
    if ('speechSynthesis' in window && text.trim()) {
      // Create a new utterance
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Set voice parameters
      utterance.rate = voiceParams.speed;
      utterance.pitch = voiceParams.pitch;
      
      // Speak the text
      window.speechSynthesis.speak(utterance);
      
      // Add artificial pause if tempo > 0
      if (voiceParams.tempo > 0) {
        // Calculate pause time in milliseconds (0-2000ms)
        const pauseTime = voiceParams.tempo * 2000;
        
        // Use speechSynthesis.pause() and resume() to create an artificial pause
        if (pauseTime > 10) { // Only pause if it's a meaningful duration
          setTimeout(() => {
            if ('speechSynthesis' in window) {
              window.speechSynthesis.pause();
              setTimeout(() => {
                if ('speechSynthesis' in window) {
                  window.speechSynthesis.resume();
                }
              }, pauseTime);
            }
          }, 10); // Short delay before pausing
        }
      }
    }
  };

  // handleGenerate resets current text and connects to the stream,
  // including the current parameter values in the query string.
  const handleGenerate = () => {
    // Reset the current text and tokens
    currentTextRef.current = "";
    setCurrentText("");
    currentTokensRef.current = [];
    setCurrentTokens([]);

    // Cancel any ongoing speech when starting a new generation
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }

    // Prevent duplicate connections
    if (eventSourceRef.current) return;

    if (!currentContext) {
      console.error("No context available for generation");
      return;
    }

    // Build a query string based on the current parameter values
    const queryParams = new URLSearchParams({
      context: currentContext,
      temperature: params.temperature.toString(),
      top_p: params.top_p.toString(),
      top_k: params.top_k.toString(),
      num_predict: params.num_predict.toString(),
      repeat_penalty: params.repeat_penalty.toString(),
      presence_penalty: params.presence_penalty.toString(),
      frequency_penalty: params.frequency_penalty.toString(),
      mirostat_mode: params.mirostat_mode.toString(),
      mirostat_tau: params.mirostat_tau.toString(),
      mirostat_eta: params.mirostat_eta.toString(),
    });

    // Open a connection to the stream endpoint with the query parameters.
    const eventSource = new EventSource(
      `${API_BASE}/stream?${queryParams.toString()}`
    );
    eventSourceRef.current = eventSource;
    setIsConnected(true);

    // Handle regular text messages for backward compatibility
    eventSource.onmessage = (event) => {
      currentTextRef.current += event.data;
      setCurrentText(currentTextRef.current);
      
      // Speak the new chunk of text as it arrives
      if (event.data.trim()) {
        speakText(event.data);
      }
    };

    // Handle the new token_data events with detailed information
    eventSource.addEventListener("token_data", (event) => {
      try {
        const tokenData: TokenData = JSON.parse(event.data);
        
        // Add the token to our tokens array with its data
        const newToken: GeneratedToken = {
          text: tokenData.text,
          data: tokenData
        };
        
        currentTokensRef.current = [...currentTokensRef.current, newToken];
        setCurrentTokens(currentTokensRef.current);
      } catch (error) {
        console.error("Error parsing token data:", error);
      }
    });

    eventSource.addEventListener("done", () => {
      // Save the completed generation in past responses.
      setGenerations((prev) => {
        const newGeneration: Generation = {
          text: currentTextRef.current,
          color: colors[prev.length % colors.length],
          params: {
            ...params,  // Include all model parameters
          },
          tokens: currentTokensRef.current  // Store the tokens with their data
        };
        return [...prev, newGeneration];
      });
      eventSource.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    });

    eventSource.addEventListener("error", (event) => {
      console.error("EventSource error:", event);
      eventSource.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    });
  };

  //Clean up speech when component unmounts
  useEffect(() => {
    return () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

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

  return { generations, currentText, currentTokens, isConnected, handleGenerate };
}

// Add this component to display tokens with probabilities
const TokenDisplay = ({ token, enableHover }: { token: GeneratedToken; enableHover: boolean }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  
  return (
    <span 
      className="token"
      style={{ 
        position: 'relative',
        display: 'inline-block',
      }}
      onMouseEnter={enableHover ? () => setShowTooltip(true) : undefined}
      onMouseLeave={enableHover ? () => setShowTooltip(false) : undefined}
    >
      <span>
        {token.text}
        <sub style={{ 
          fontSize: '0.6em', 
          color: '#888', 
          marginLeft: '1px' 
        }}>
          {Math.round(token.data.prob * 100)}%
        </sub>
      </span>
      
      {showTooltip && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          padding: '8px',
          borderRadius: '4px',
          fontSize: '0.8rem',
          zIndex: 2000,
          width: 'max-content',
          maxWidth: '200px',
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.3)',
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Top Candidates:</div>
          {token.data.top5.map((candidate, idx) => (
            <div key={idx} style={{
              display: 'flex',
              justifyContent: 'space-between',
              padding: '2px 0',
              borderTop: idx > 0 ? '1px solid rgba(255, 255, 255, 0.1)' : 'none',
            }}>
              <span style={{ 
                color: candidate.id === token.data.id ? '#ffca28' : 'white',
                fontWeight: candidate.id === token.data.id ? 'bold' : 'normal',
              }}>
                {candidate.text || "<empty>"}
              </span>
              <span style={{ marginLeft: '8px' }}>
                {Math.round(candidate.prob * 100)}%
              </span>
            </div>
          ))}
        </div>
      )}
    </span>
  );
};

// Create a component to display the whole token sequence
const TokenizedText = ({ tokens, enableHover }: { tokens: GeneratedToken[]; enableHover: boolean }) => {
  if (!tokens || tokens.length === 0) {
    return <span></span>;
  }
  
  return (
    <div>
      {tokens.map((token, idx) => (
        <TokenDisplay key={idx} token={token} enableHover={enableHover} />
      ))}
    </div>
  );
};

const LlamaStream = () => {
  const location = useLocation();
  const initialPrompt = location.state?.prompt;

  // If no prompt was provided, redirect back to landing page
  if (!initialPrompt) {
    return <Navigate to="/" replace />;
  }

  const [params, setParams] = useState<Params>({
    temperature: 0.7,
    top_p: 0.9,
    top_k: 40,
    num_predict: 4,
    repeat_penalty: 1.1,
    presence_penalty: 0.0,
    frequency_penalty: 0.0,
    mirostat_mode: 0,     // Default to disabled
    mirostat_tau: 5.0,    // Default tau value
    mirostat_eta: 0.1,    // Default eta value
  });
  
  // Add voice parameters state
  const [voiceParams, setVoiceParams] = useState<VoiceParams>({
    pitch: 1.0,    // Default pitch (normal)
    speed: 4.0,    // Fast speech (keeping the old speed)
    tempo: 0.0,    // Minimal pause between chunks
  });

  const [isPaused, setIsPaused] = useState(false);
  const [currentContext] = useState(initialPrompt);

  const togglePause = () => {
    setIsPaused(prevPaused => !prevPaused);
  };

  const updateParameter = (paramName: keyof Params, value: number) => {
    setParams((prev) => ({
      ...prev,
      [paramName]: value,
    }));
  };

  const updateVoiceParameter = (paramName: keyof VoiceParams, value: number) => {
    setVoiceParams((prev) => ({
      ...prev,
      [paramName]: value,
    }));
  };
// omg
  const { generations, currentText, currentTokens } = useStreamingGenerations(
    params, 
    isPaused, 
    currentContext,
    voiceParams
  );

  const isMirostatEnabled = params.mirostat_mode > 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
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
          
          /* Add responsive breakpoint */
          @media (max-width: 768px) {
            .content-container {
              flex-direction: column !important;
            }
            .sidebar {
              flex: 1 1 auto !important;
              width: 100% !important;
              margin-bottom: 16px;
            }
            .main-content {
              flex: 1 1 auto !important;
              width: 100% !important;
            }
          }
          
          /* Token display styles */
          .token {
            position: relative;
            display: inline-block;
          }
          
          .token:hover {
            background-color: rgba(0, 0, 0, 0.05);
            border-radius: 4px;
          }
          
          /* Tooltip animations */
          @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
          }
          
          .token-tooltip {
            animation: fadeIn 0.2s;
          }
        `}
      </style>

      <div style={{
        width: "100vw",
        padding: "1rem",
        background: "linear-gradient(45deg, #2b1331, #000000)",
        marginBottom: "1rem",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "0.5rem"
      }}>
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

      <div 
        className="content-container" 
        style={{
          display: "flex",
          width: "100%",
          flex: 1,
          padding: "1rem",
          gap: "16px",
        }}
      >
        <div 
          className="left-sidebar"
          style={{ 
            flex: "0 0 250px"
          }}
        >
          <Space direction="vertical" style={{ width: '100%', gap: '16px' }}>
            <Card title="Prompt: ">
              <div style={{ 
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
            </Card>

            <Card title="Voice Parameters">
              <Space direction="vertical" style={{ width: '100%', display: 'flex', alignItems: 'flex-start' }}>
                <div style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Speech Speed: </span>
                    <span>{voiceParams.speed.toFixed(1)}</span>
                  </div>
                  <Slider
                    min={0.5}
                    max={5.0}
                    step={0.1}
                    value={voiceParams.speed}
                    onChange={(value: number) => updateVoiceParameter("speed", value)}
                    style={{ width: '100%' }}
                  />
                </div>
                
                <div style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Pitch: </span>
                    <span>{voiceParams.pitch.toFixed(1)}</span>
                  </div>
                  <Slider
                    min={0.5}
                    max={2.0}
                    step={0.1}
                    value={voiceParams.pitch}
                    onChange={(value: number) => updateVoiceParameter("pitch", value)}
                    style={{ width: '100%' }}
                  />
                </div>
                
                <div style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Tempo (Pause): </span>
                    <span>{(voiceParams.tempo * 2000).toFixed(0)}ms</span>
                  </div>
                  <Slider
                    min={0}
                    max={1}
                    step={0.01}
                    value={voiceParams.tempo}
                    onChange={(value: number) => updateVoiceParameter("tempo", value)}
                    style={{ width: '100%' }}
                  />
                </div>
              </Space>
            </Card>

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
        </div>

        <div 
          className="main-content"
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: "16px",
            height: "100%",
            minHeight: 0,
          }}
        >
          <Card 
            title="Current Response" 
            style={{ 
              height: "300px",
              marginBottom: "16px"
            }}
          >
            <div style={{
              height: "250px",
              wordWrap: "break-word",
              whiteSpace: "pre-wrap",
              overflow: "auto"
            }}>
              {currentTokens.length > 0 ? (
                <TokenizedText tokens={currentTokens} enableHover={true} />
              ) : (
                currentText
              )}
            </div>
          </Card>

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
                const maxSlots = 15;
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
                        <div style={{
                          wordWrap: "break-word",
                          whiteSpace: "pre-wrap"
                        }}>
                          {gen.tokens && gen.tokens.length > 0 ? (
                            <TokenizedText tokens={gen.tokens} enableHover={true} />
                          ) : (
                            gen.text
                          )}
                        </div>
                        <div style={{
                          marginTop: '8px',
                          padding: '8px',
                          borderTop: '1px solid #eee',
                          fontSize: '0.85em',
                          color: '#666',
                        }}>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            <span>temp: {gen.params.temperature.toFixed(2)}</span>
                            {gen.params.mirostat_mode > 0 ? (
                              <>
                                <span>mirostat: {gen.params.mirostat_mode}</span>
                                <span>tau: {gen.params.mirostat_tau.toFixed(1)}</span>
                                <span>eta: {gen.params.mirostat_eta.toFixed(3)}</span>
                              </>
                            ) : (
                              <>
                                <span>top_p: {gen.params.top_p.toFixed(2)}</span>
                                <span>top_k: {gen.params.top_k}</span>
                              </>
                            )}
                            <span>repeat: {gen.params.repeat_penalty.toFixed(2)}</span>
                            <span>presence: {gen.params.presence_penalty.toFixed(2)}</span>
                            <span>frequency: {gen.params.frequency_penalty.toFixed(2)}</span>
                            <span>tokens: {gen.params.num_predict}</span>
                          </div>
                        </div>
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

        <div 
          className="right-sidebar"
          style={{ 
            flex: "0 0 250px"
          }}
        >
          <Card title="Model Parameters">
            <Space direction="vertical" style={{ width: '100%', display: 'flex', alignItems: 'flex-start' }}>
              <div style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Temperature: </span>
                  <span>{params.temperature.toFixed(2)}</span>
                </div>
                <Slider
                  min={0}
                  max={1}
                  step={0.01}
                  value={params.temperature}
                  onChange={(value: number) => updateParameter("temperature", value)}
                  style={{ width: '100%' }}
                />
              </div>
              
              <div style={{ width: '100%' }}>
                <span>Mirostat Mode: </span>
                <Select
                  value={params.mirostat_mode}
                  onChange={(value: number) => updateParameter("mirostat_mode", value)}
                  style={{ width: '100%' }}
                >
                  <Select.Option value={0}>Disabled</Select.Option>
                  <Select.Option value={1}>Mirostat</Select.Option>
                  <Select.Option value={2}>Mirostat 2.0</Select.Option>
                </Select>
              </div>
              
              {isMirostatEnabled && (
                <>
                  <div style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Mirostat Tau: </span>
                      <span>{params.mirostat_tau.toFixed(1)}</span>
                    </div>
                    <Slider
                      min={1.0}
                      max={10.0}
                      step={0.1}
                      value={params.mirostat_tau}
                      onChange={(value: number) => updateParameter("mirostat_tau", value)}
                      style={{ width: '100%' }}
                    />
                  </div>
                  <div style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Mirostat Eta: </span>
                      <span>{params.mirostat_eta.toFixed(3)}</span>
                    </div>
                    <Slider
                      min={0.001}
                      max={1.0}
                      step={0.001}
                      value={params.mirostat_eta}
                      onChange={(value: number) => updateParameter("mirostat_eta", value)}
                      style={{ width: '100%' }}
                    />
                  </div>
                </>
              )}
              
              <div style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Top_p: </span>
                  <span>{params.top_p.toFixed(2)}</span>
                </div>
                <Slider
                  min={0}
                  max={1}
                  step={0.01}
                  value={params.top_p}
                  onChange={(value: number) => updateParameter("top_p", value)}
                  disabled={isMirostatEnabled}
                  style={{ width: '100%' }}
                />
              </div>
              <div style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Top_k: </span>
                  <span>{params.top_k}</span>
                </div>
                <Slider
                  min={1}
                  max={100}
                  step={1}
                  value={params.top_k}
                  onChange={(value: number) => updateParameter("top_k", value)}
                  disabled={isMirostatEnabled}
                  style={{ width: '100%' }}
                />
              </div>
              <div style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Repeat Penalty: </span>
                  <span>{params.repeat_penalty.toFixed(2)}</span>
                </div>
                <Slider
                  min={1.0}
                  max={2.0}
                  step={0.05}
                  value={params.repeat_penalty}
                  onChange={(value: number) => updateParameter("repeat_penalty", value)}
                  style={{ width: '100%' }}
                />
              </div>
              <div style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Presence Penalty: </span>
                  <span>{params.presence_penalty.toFixed(2)}</span>
                </div>
                <Slider
                  min={0.0}
                  max={1.0}
                  step={0.05}
                  value={params.presence_penalty}
                  onChange={(value: number) => updateParameter("presence_penalty", value)}
                  style={{ width: '100%' }}
                />
              </div>
              <div style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Frequency Penalty: </span>
                  <span>{params.frequency_penalty.toFixed(2)}</span>
                </div>
                <Slider
                  min={0.0}
                  max={1.0}
                  step={0.05}
                  value={params.frequency_penalty}
                  onChange={(value: number) => updateParameter("frequency_penalty", value)}
                  style={{ width: '100%' }}
                />
              </div>
              <div style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Tokens to Generate: </span>
                  <span>{params.num_predict}</span>
                </div>
                <Slider
                  min={4}
                  max={128}
                  step={4}
                  value={params.num_predict}
                  onChange={(value: number) => updateParameter("num_predict", value)}
                  style={{ width: '100%' }}
                />
              </div>
            </Space>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default LlamaStream;