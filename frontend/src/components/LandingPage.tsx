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
      background: "linear-gradient(45deg, #2b1331, #000000)",
      padding: "1rem",
      boxSizing: "border-box",
      overflow: "auto"
    }}>
      <div style={{
        width: "100%",
        maxWidth: "1200px",
        background: "rgba(255, 255, 255, 0.95)",
        borderRadius: "16px",
        padding: "2rem",
        boxShadow: "0 8px 32px rgba(0, 0, 0, 0.2)",
        display: "flex",
        flexDirection: "column",
        gap: "1.5rem",
        boxSizing: "border-box",
        marginTop: "1rem"
      }}>
        <div style={{
          fontSize: "1.2rem",
          color: "#333",
          textAlign: "left",
          lineHeight: "1.6"
        }}>
          <div style={{
            fontSize: "1.8rem",
            fontWeight: "bold",
            marginBottom: "1rem",
            color: "#7700ff"
          }}>
            WORD SYNTH
          </div>
          
          Just like a synthesizer allows you to manipulate sound in real time with knobs and sliders, word synth lets you manipulate generations of a Llama3.2 1B model in real time via exposed sampling parameters.

          <p style={{ marginTop: "1rem", marginBottom: "0.5rem" }}>Things to Try:</p>
          <ul style={{ 
            paddingLeft: "1.5rem",
            marginBottom: "1rem"
          }}>
            <li>Set temp, top_p or top_k all the way down and see it become deterministic.</li>
            <li>Set top_k to 2 and observe that you only see two first tokens</li>
            <li>Tell the model to say something over and over again and then adjust the presence or repeat Penalty</li>
            <li>See if you can 'crash' the model into giving you nonsense</li>
          </ul>

        </div>

        <div style={{
          fontSize: "1rem",
          color: "#555",
          textAlign: "left",
          marginBottom: "0.5rem"
        }}>
          Enter your prompt to begin:
        </div>

        <Input.TextArea
          value={inputPrompt}
          onChange={(e) => setInputPrompt(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Enter your prompt here..."
          autoSize={{ minRows: 4, maxRows: 8 }}
          style={{
            fontSize: "1rem",
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
            height: "50px",
            fontSize: "1.2rem",
            background: "linear-gradient(45deg, #e100ff, #7700ff)",
            border: "none",
            borderRadius: "8px",
            marginTop: "0.5rem",
            width: "100%"
          }}
        >
          START
        </Button>

        <div style={{
          display: "flex",
          justifyContent: "flex-start",
          gap: "1rem",
          marginTop: "0.5rem"
        }}>
          <a
            href="https://github.com/jakesimonds/wordSynth"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: "#7700ff",
              textDecoration: "none",
              fontSize: "0.9rem",
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
              fontSize: "0.9rem",
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