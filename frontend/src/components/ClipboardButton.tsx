import { useState } from 'react';
import { Button, Typography } from 'antd';

const { Text } = Typography;

interface ClipboardLifelineProps {
  buttonText?: string;
  appContext?: string;
  onCopy?: (text: string) => void;
  bannerMode?: boolean;
}

const DEFAULT_CONTEXT = `This is WordSynth, a web app for exploring Llama 3.2 1B text generation with real-time parameter controls. The user below is seeking help or clarification:`;

const ClipboardLifeline: React.FC<ClipboardLifelineProps> = ({
  buttonText = "Copy to clipboard",
  appContext = DEFAULT_CONTEXT,
  onCopy,
  bannerMode = false,
}) => {
  const [copied, setCopied] = useState(false);

  const getClipboardText = () => {
    return `${appContext}\nUser's question: [No question entered]`;
  };

  const handleCopy = async () => {
    const textToCopy = getClipboardText();
    try {
      await navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      onCopy?.(textToCopy);
      setTimeout(() => setCopied(false), 1500);
    } catch (err) {
      setCopied(false);
    }
  };

  if (bannerMode) {
    return (
      <div
        style={{
          width: '100%',
          background: 'linear-gradient(90deg, #f8f8ff 60%, #e6e6fa 100%)',
          borderBottom: '2px solid #b19dd8',
          boxShadow: '0 2px 12px rgba(80,40,120,0.07)',
          padding: '18px 4vw',
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 24,
          zIndex: 10,
          position: 'relative',
          flexWrap: 'wrap',
        }}
      >
        <Text
          strong
          style={{
            fontSize: 'clamp(1.5rem, 4vw, 2.5rem)',
            color: '#5a3d8a',
            textAlign: 'center',
            letterSpacing: 2,
            textTransform: 'uppercase',
            textShadow: '0 2px 12px rgba(90,61,138,0.10)',
            lineHeight: 1.1,
            fontWeight: 900,
            flex: '0 0 auto',
            marginRight: 16,
            marginBottom: 0,
            whiteSpace: 'nowrap',
          }}
        >
          Premium Context
        </Text>
        <Button
          type="primary"
          onClick={handleCopy}
          style={{
            padding: '18px 36px',
            fontSize: '1.5rem',
            backgroundColor: copied ? '#52c41a' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontWeight: 900,
            boxShadow: '0 4px 24px 0 rgba(40,167,69,0.18)',
            letterSpacing: 1.2,
            flex: '0 0 auto',
            margin: '0 16px',
            minWidth: 220,
            minHeight: 0,
            whiteSpace: 'nowrap',
          }}
        >
          {copied ? 'Copied!' : buttonText}
        </Button>
        <Text
          type="secondary"
          style={{
            fontSize: 14,
            textAlign: 'right',
            flex: '1 1 0',
            minWidth: 120,
            marginLeft: 16,
            marginTop: 0,
            opacity: 0.8,
            whiteSpace: 'normal',
            wordBreak: 'break-word',
          }}
        >
          1: Click button. 2: Go to LLM of your choice. 3: Paste.
        </Text>
        <style>{`
          @media (max-width: 700px) {
            .premium-context-banner {
              flex-direction: column !important;
              align-items: stretch !important;
              text-align: center !important;
              gap: 10px !important;
            }
            .premium-context-banner .ant-typography {
              margin-right: 0 !important;
              margin-left: 0 !important;
              margin-bottom: 0 !important;
              white-space: normal !important;
            }
            .premium-context-banner .ant-btn {
              margin: 0 auto 0 auto !important;
              min-width: 180px !important;
              width: 100% !important;
            }
          }
        `}</style>
      </div>
    );
  }

  // Non-banner mode (not used for now)
  return null;
};

export default ClipboardLifeline; 