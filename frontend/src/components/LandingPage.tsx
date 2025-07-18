import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Select } from "antd";
import ClipboardLifeline from './ClipboardButton';

const LandingPage = () => {
  // Predefined options
  const promptOptions = [
    "Tell me a joke, please.",
    "Repeat the word hello over and over again 100 times.",
    "Who is Ned Flanders?",
    "What is Domain Driven Design?",
    "<div>hello world</div>"
  ];

  const hotWordOptions = [
    "banana",
    "the",
    "ch",
    "and",
    "interesting"
  ];

  const [inputPrompt, setInputPrompt] = useState(promptOptions[0]);
  const [hotWord, setHotWord] = useState(hotWordOptions[0]);
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

  return (
    <div style={{
      minHeight: "100vh",
      width: "100%",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "flex-start",
      background: "linear-gradient(45deg, #2b1331, #000000)",
      padding: isMobile ? "0.5rem" : "2rem",
      boxSizing: "border-box",
      overflow: isMobile ? "hidden" : "auto",
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0
    }}>
      <ClipboardLifeline bannerMode />
      <div style={{
        width: "100%",
        maxWidth: isMobile ? "100%" : "1200px",
        maxHeight: isMobile ? "90vh" : "none",
        overflowY: isMobile ? "auto" : "visible",
        background: "rgba(255, 255, 255, 0.95)",
        borderRadius: isMobile ? "12px" : "16px",
        padding: isMobile ? "1rem" : "2.5rem",
        boxShadow: "0 8px 32px rgba(0, 0, 0, 0.2)",
        display: "flex",
        flexDirection: "column",
        gap: isMobile ? "0.75rem" : "1.5rem",
        boxSizing: "border-box",
        margin: isMobile ? "auto" : "1rem auto"
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


        </div>

        <div style={{
          fontSize: isMobile ? "0.9rem" : "1.1rem",
          color: "#555",
          textAlign: "left",
          marginBottom: isMobile ? "0.15rem" : "0.5rem"
        }}>
          <b>Select a prompt:</b>
        </div>

        <Select
          value={inputPrompt}
          onChange={(value) => setInputPrompt(value)}
          style={{
            width: "100%",
            fontSize: isMobile ? "0.9rem" : "1.1rem",
          }}
          size={isMobile ? "middle" : "large"}
          options={promptOptions.map(prompt => ({
            value: prompt,
            label: prompt,
          }))}
          optionLabelProp="label"
          optionRender={(option) => (
            <div style={{ 
              whiteSpace: "normal", 
              wordBreak: "break-word",
              padding: "4px 0"
            }}>
              {option.label}
            </div>
          )}
          maxTagTextLength={100}
        />

        <div style={{
          fontSize: isMobile ? "0.9rem" : "1.1rem",
          color: "#555",
          textAlign: "left",
          marginBottom: isMobile ? "0.15rem" : "0.5rem",
          marginTop: isMobile ? "0.35rem" : "0.75rem"
        }}>
          <b>Select a Hot Word/Token:</b>
        </div>

        <Select
          value={hotWord}
          onChange={(value) => setHotWord(value)}
          style={{
            width: "100%",
            fontSize: isMobile ? "0.9rem" : "1.1rem",
          }}
          size={isMobile ? "middle" : "large"}
          options={hotWordOptions.map(word => ({
            value: word,
            label: word
          }))}
        />

        <small style={{
          fontSize: isMobile ? "0.8rem" : "1rem",
          color: "#666",
          textAlign: "left",
          marginBottom: isMobile ? "0.15rem" : "0.5rem"
        }}>
          You'll be able to adjust the probability of this token with a slider. 
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
            marginTop: isMobile ? "0.15rem" : "0.75rem",
            width: "100%"
          }}
        >
          START
        </Button>

        <div style={{
          display: "flex",
          justifyContent: "flex-start",
          gap: "1rem",
          marginTop: isMobile ? "0.15rem" : "0.75rem"
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