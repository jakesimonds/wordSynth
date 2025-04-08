import { useState, KeyboardEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Input, Button } from "antd";

const LandingPage = () => {
  const [inputPrompt, setInputPrompt] = useState("Repeat the word hello over and over again 100 times.");
  const navigate = useNavigate();

  const handleStart = () => {
    // Navigate to the main app with the prompt as a state
    navigate('/app', { state: { prompt: inputPrompt } });
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
      justifyContent: "center",
      background: "linear-gradient(45deg, #2b1331, #000000)",
      padding: "1rem",
      boxSizing: "border-box",
      overflow: "hidden"
    }}>
      <h1 style={{
        margin: "1rem 0",
        fontSize: "clamp(2.5rem, 8vw, 4.5rem)", // Responsive font size
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
        width: "95vw",
        //maxWidth: "500px", // Slightly reduced max-width
        background: "rgba(255, 255, 255, 0.95)",
        borderRadius: "16px",
        padding: "1.5rem", // Reduced padding
        boxShadow: "0 8px 32px rgba(0, 0, 0, 0.2)",
        display: "flex",
        flexDirection: "column",
        gap: "1rem", // Reduced gap
        boxSizing: "border-box"
      }}>
        <div style={{
          fontSize: "clamp(1rem, 4vw, 1.5rem)", // Responsive font size
          color: "#333",
          textAlign: "center",
          lineHeight: "1.6"
        }}>
          Welcome to Word Synth, where text meets voice in real-time synthesis.
        </div>

        <div style={{
          fontSize: "clamp(1rem, 4vw, 1.2rem)", // Responsive font size
          color: "#555",
          textAlign: "center",
          marginBottom: "0.5rem"
        }}>
          Enter your prompt to begin:
        </div>

        <Input.TextArea
          value={inputPrompt}
          onChange={(e) => setInputPrompt(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Enter your prompt here..."
          autoSize={{ minRows: 4, maxRows: 8 }} // Adjusted for mobile
          style={{
            fontSize: "clamp(1rem, 4vw, 1.2rem)", // Responsive font size
            borderRadius: "8px",
            border: "2px solid #e100ff33",
            width: "100%",
            boxSizing: "border-box"
          }}
        />

        <Button
          type="primary"
          onClick={handleStart}
          size="large"
          style={{
            height: "50px", // Slightly smaller on mobile
            fontSize: "clamp(1rem, 4vw, 1.4rem)", // Responsive font size
            background: "linear-gradient(45deg, #e100ff, #7700ff)",
            border: "none",
            borderRadius: "8px",
            marginTop: "0.5rem",
            width: "100%"
          }}
        >
          Start Generating
        </Button>

        <div style={{
          display: "flex",
          justifyContent: "center",
          gap: "1rem",
          marginTop: "0.5rem"
        }}>
          <a
            href="https://github.com/jakesimonds/wordSynth"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: "#b19dd8",
              textDecoration: "none",
              fontSize: "clamp(0.8rem, 3vw, 1.1rem)", // Responsive font size
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
              fontSize: "clamp(0.8rem, 3vw, 1.1rem)", // Responsive font size
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