// A simple simulation of speech synthesis for Node.js
// This doesn't actually produce sound, but demonstrates the logic flow

// Mock speechSynthesis object
const speechSynthesis = {
    speaking: false,
    paused: false,
    pending: [],
    
    speak(utterance) {
      console.log(`[SPEECH] Would speak: "${utterance.text}"`);
      this.pending.push(utterance);
      this.processQueue();
    },
    
    cancel() {
      console.log('[SPEECH] Cancelled all speech');
      this.pending = [];
      this.speaking = false;
    },
    
    pause() {
      if (this.speaking) {
        console.log('[SPEECH] Paused speech');
        this.paused = true;
      }
    },
    
    resume() {
      if (this.paused) {
        console.log('[SPEECH] Resumed speech');
        this.paused = false;
        this.processQueue();
      }
    },
    
    processQueue() {
      if (!this.speaking && !this.paused && this.pending.length > 0) {
        this.speaking = true;
        const utterance = this.pending.shift();
        
        console.log(`[SPEECH] Started speaking: "${utterance.text}"`);
        
        // Simulate speech duration (1 second per 5 characters)
        const duration = Math.max(1000, utterance.text.length * 200);
        
        setTimeout(() => {
          console.log(`[SPEECH] Finished speaking: "${utterance.text}"`);
          this.speaking = false;
          
          // Call onend if it exists
          if (utterance.onend) {
            utterance.onend();
          }
          
          // Process next item in queue
          this.processQueue();
        }, duration);
      }
    }
  };
  
  // Mock SpeechSynthesisUtterance class
  class SpeechSynthesisUtterance {
    constructor(text) {
      this.text = text;
      this.rate = 1.0;
      this.pitch = 1.0;
      this.volume = 1.0;
      this.onstart = null;
      this.onend = null;
      this.onerror = null;
    }
  }
  
  // Attach to global scope to mimic browser environment
  global.speechSynthesis = speechSynthesis;
  global.SpeechSynthesisUtterance = SpeechSynthesisUtterance;
  
  // Function to speak text
  function speak(text) {
    console.log(`\nRequesting to speak: "${text}"`);
    
    // Cancel any ongoing speech
    speechSynthesis.cancel();
    
    // Create a new utterance
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set up event handlers
    utterance.onend = () => {
      console.log('Speech ended event fired');
    };
    
    // Speak the text
    speechSynthesis.speak(utterance);
  }
  
  // Test the speech functionality
  console.log('=== Speech Synthesis Test ===');
  
  // Speak "Hello World" immediately
  speak('Hello World');
  
  // Speak a series of phrases with delays
  setTimeout(() => speak('Hello World again'), 2000);
  setTimeout(() => speak('This is a test of speech synthesis'), 4000);
  setTimeout(() => speak('Each phrase interrupts the previous one'), 6000);
  setTimeout(() => speak('This demonstrates how the speech API works'), 8000);
  
  // Demonstrate speech cancellation
  setTimeout(() => {
    console.log('\nCancelling all speech...');
    speechSynthesis.cancel();
  }, 10000);
  
  setTimeout(() => speak('Speech resumed after cancellation'), 11000);
  
  // Keep the process running for the duration of our test
  setTimeout(() => {
    console.log('\n=== Test Complete ===');
  }, 15000);