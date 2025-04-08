import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input, Button } from "antd";

const LandingPage = () => {
  const [inputPrompt, setInputPrompt] = useState("Repeat the word hello over and over again 100 times.");
  const navigate = useNavigate();

  const handleStart = () => {
    // Navigate to the main app with the prompt as a state
    navigate('/app', { state: { prompt: inputPrompt } });
  };

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      background: "linear-gradient(45deg, #2b1331, #000000)",
      padding: "2rem"
    }}>
      <h1 style={{
        margin: "2rem 0",
        fontSize: "4.5rem",
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
        width: "80%",
        maxWidth: "800px",
        background: "rgba(255, 255, 255, 0.95)",
        borderRadius: "16px",
        padding: "2rem",
        boxShadow: "0 8px 32px rgba(0, 0, 0, 0.2)",
        display: "flex",
        flexDirection: "column",
        gap: "2rem"
      }}>
        <div style={{
          fontSize: "1.5rem",
          color: "#333",
          textAlign: "center",
          lineHeight: "1.6"
        }}>
          Welcome to Word Synth, where text meets voice in real-time synthesis.
        </div>

        <div style={{
          fontSize: "1.2rem",
          color: "#555",
          textAlign: "center",
          marginBottom: "1rem"
        }}>
          Enter your prompt to begin:
        </div>

        <Input.TextArea
          value={inputPrompt}
          onChange={(e) => setInputPrompt(e.target.value)}
          placeholder="Enter your prompt here..."
          autoSize={{ minRows: 6, maxRows: 10 }}
          style={{
            fontSize: "1.2rem",
            borderRadius: "8px",
            border: "2px solid #e100ff33",
          }}
        />

        <Button
          type="primary"
          onClick={handleStart}
          size="large"
          style={{
            height: "60px",
            fontSize: "1.4rem",
            background: "linear-gradient(45deg, #e100ff, #7700ff)",
            border: "none",
            borderRadius: "8px",
            marginTop: "1rem"
          }}
        >
          Start Generating
        </Button>

        <div style={{
          display: "flex",
          justifyContent: "center",
          gap: "2rem",
          marginTop: "1rem"
        }}>
          <a
            href="https://github.com/jakesimonds/wordSynth"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: "#b19dd8",
              textDecoration: "none",
              fontSize: "1.1rem",
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
              color: "#b19dd8",
              textDecoration: "none",
              fontSize: "1.1rem",
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