import { useState, KeyboardEvent, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Input, Button } from "antd";

const LandingPage = () => {
  const [inputPrompt, setInputPrompt] = useState("Repeat the word hello over and over again 100 times.");
  const [hotWord, setHotWord] = useState('the');
  const [isMobile, setIsMobile] = useState(false);
  const navigate = useNavigate();

  // Detect if device is mobile
  useEffect(() => {
    const checkIfMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkIfMobile();
    window.addEventListener('resize', checkIfMobile);
    return () => window.removeEventListener('resize', checkIfMobile);
  }, []);

  const handleStart = () => {
    // Navigate to the main app with the prompt and hot word as states
    navigate('/app', { state: { prompt: inputPrompt, hotWord } });
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent default Enter key behavior
      handleStart();
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      width: "100%",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      background: "linear-gradient(45deg, #2b1331, #000000)",
      padding: isMobile ? "0.5rem" : "2rem",
      boxSizing: "border-box",
      overflow: "auto"
    }}>
      <div style={{
        width: "100%",
        maxWidth: isMobile ? "100%" : "1200px",
        background: "rgba(255, 255, 255, 0.95)",
        borderRadius: isMobile ? "12px" : "16px",
        padding: isMobile ? "1rem" : "2.5rem",
        boxShadow: "0 8px 32px rgba(0, 0, 0, 0.2)",
        display: "flex",
        flexDirection: "column",
        gap: isMobile ? "1rem" : "1.5rem",
        boxSizing: "border-box",
        marginTop: isMobile ? "0.5rem" : "1rem"
      }}>
        <div style={{
          fontSize: isMobile ? "1rem" : "1.2rem",
          color: "#333",
          textAlign: "left",
          lineHeight: isMobile ? "1.4" : "1.6"
        }}>
          <div style={{
            fontSize: isMobile ? "1.4rem" : "2rem",
            fontWeight: "bold",
            marginBottom: isMobile ? "0.5rem" : "1rem",
            color: "#7700ff"
          }}>
            WORD SYNTH
          </div>
          
          Just like a synthesizer allows you to manipulate sound in real time with knobs and sliders, Word Synth lets you manipulate generations of a Llama3.2 1B model in real time via exposed sampling parameters.

          <p style={{ marginTop: isMobile ? "0.75rem" : "1.25rem", marginBottom: isMobile ? "0.25rem" : "0.75rem" }}>Things to Try:</p>
          <ul style={{ 
            paddingLeft: isMobile ? "1.25rem" : "2rem",
            marginBottom: isMobile ? "0.75rem" : "1.25rem",
            marginTop: "0"
          }}>
            <li>Set temp, top_p or top_k all the way down and see it become deterministic.</li>
            <li>Set top_k to 2 and observe that you only see two first tokens</li>
            <li>Tell the model to say something over and over again and then adjust the presence or repeat Penalty</li>
            <li>See if you can 'crash' the model into giving you nonsense</li>
          </ul>
        </div>

        <div style={{
          fontSize: isMobile ? "0.9rem" : "1.1rem",
          color: "#555",
          textAlign: "left",
          marginBottom: isMobile ? "0.25rem" : "0.5rem"
        }}>
          Enter your prompt to begin:
        </div>

        <Input.TextArea
          value={inputPrompt}
          onChange={(e) => setInputPrompt(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Enter your prompt here..."
          autoSize={{ minRows: isMobile ? 3 : 4, maxRows: isMobile ? 6 : 8 }}
          style={{
            fontSize: isMobile ? "0.9rem" : "1.1rem",
            borderRadius: "8px",
            border: "2px solid #e100ff33",
            width: "100%",
            boxSizing: "border-box"
          }}
        />

        <div style={{
          fontSize: isMobile ? "0.9rem" : "1.1rem",
          color: "#555",
          textAlign: "left",
          marginBottom: isMobile ? "0.25rem" : "0.5rem"
        }}>
          Hot Word (will be boosted during generation):
        </div>

        <Input
          value={hotWord}
          onChange={(e) => setHotWord(e.target.value)}
          placeholder="Enter a word to boost"
          style={{
            fontSize: isMobile ? "0.9rem" : "1.1rem",
            borderRadius: "8px",
            border: "2px solid #e100ff33",
            width: "100%",
            boxSizing: "border-box"
          }}
        />

        <small style={{
          fontSize: isMobile ? "0.8rem" : "1rem",
          color: "#666",
          textAlign: "left",
          marginBottom: isMobile ? "0.25rem" : "0.5rem"
        }}>
          For best results, use a single word like "the", "and", or "fantastic"
        </small>

        <Button
          type="primary"
          onClick={handleStart}
          size="large"
          style={{
            height: isMobile ? "40px" : "50px",
            fontSize: isMobile ? "1rem" : "1.2rem",
            background: "linear-gradient(45deg, #e100ff, #7700ff)",
            border: "none",
            borderRadius: "8px",
            marginTop: isMobile ? "0.25rem" : "0.75rem",
            width: "100%"
          }}
        >
          START
        </Button>

        <div style={{
          display: "flex",
          justifyContent: "flex-start",
          gap: "1rem",
          marginTop: isMobile ? "0.25rem" : "0.75rem"
        }}>
          <a
            href="https://github.com/jakesimonds/wordSynth"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: "#7700ff",
              textDecoration: "none",
              fontSize: isMobile ? "0.8rem" : "1rem",
              transition: "color 0.2s"
            }}
          >
            github
          </a>
          <a
            href="https://jakesimonds.github.io/"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: "#7700ff",
              textDecoration: "none",
              fontSize: isMobile ? "0.8rem" : "1rem",
              transition: "color 0.2s"
            }}
          >
            jakesimonds
          </a>
        </div>
      </div>
    </div>
  );
};

export default LandingPage; 