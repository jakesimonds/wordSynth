import React from 'react';
import { Modal } from 'antd';

interface HelpProps {
  isVisible: boolean;
  onClose: () => void;
}

const Help: React.FC<HelpProps> = ({ isVisible, onClose }) => {
  return (
    <Modal
      title="Info"
      open={isVisible}
      onCancel={onClose}
      footer={null}
      width={800}
    >
      <div style={{ padding: '10px', fontSize: '16px', lineHeight: '1.6' }}>
        <h2>Word Synth!</h2>
        
        <p>
          If it's not working one thing to try is ctrl+q your browser...very experimental though apologies if its frustrating!
        </p>
        
        <h3>What is it?</h3>
        <ul>
          <li>This is a Llama 3.2 1B param model running via llama.cpp, with sampling parameters exposed. </li>
          <li>The 'Hot Token' is one specific token that you can turn up the probability on. So whatever the probability of that token was normally, it's magnified according to the slider.</li>
          <li>Hover over any word to see the top-5 probability logits for that token.</li>
          <li>Synth analogy: with a synth, you're changing a sound with knobs. Here, you're changing we sample from an LLM, with sliders.</li>
          <li>Change one thing at a time and see what happens!</li>
        </ul>
        <h3>Links</h3>
        <ul>
          <li><a href="https://github.com/jakesimonds/wordSynth">Code</a></li>
          <li><a href="https://jakesimonds.github.io/">me</a></li>
          <li><a href="http://latenthomer.com">Latent Homer (embedding search toy app)</a></li>
          <li><a href="https://youtu.be/rLllToK64jM">demo</a></li>
        </ul>
      </div>
    </Modal>
  );
};

export default Help; 