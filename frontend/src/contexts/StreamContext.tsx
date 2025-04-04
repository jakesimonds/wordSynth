import React, { createContext, useContext, useEffect, useState } from 'react';

const API_BASE = import.meta.env.DEV 
  ? 'http://localhost:8000' 
  : '/api';

interface StreamContextType {
    currentResponse: string;
    isStreaming: boolean;
    setupStream: () => void;
    closeStream: () => void;
}

const StreamContext = createContext<StreamContextType | undefined>(undefined);

// Changed to named function for Fast Refresh compatibility
function useStream() {
    const context = useContext(StreamContext);
    if (context === undefined) {
        throw new Error('useStream must be used within a StreamProvider');
    }
    return context;
}

// Changed to named function for Fast Refresh compatibility
function StreamProvider({ children }: { children: React.ReactNode }) {
    const [currentResponse, setCurrentResponse] = useState<string>('');
    const [isStreaming, setIsStreaming] = useState(false);
    const [eventSource, setEventSource] = useState<EventSource | null>(null);

    const setupStream = () => {
        closeStream();

        const newEventSource = new EventSource(`${API_BASE}/stream`);
        setEventSource(newEventSource);
        setIsStreaming(true);
        setCurrentResponse(''); // Clear previous response

        newEventSource.onmessage = (event) => {
            try {
                const text = event.data.toString().trim();
                setCurrentResponse(prev => {
                    // Only append if we have new text
                    if (text) {
                        return prev + text;
                    }
                    return prev;
                });
            } catch (error) {
                console.error('Error processing stream data:', error);
            }
        };

        newEventSource.addEventListener('done', () => {
            closeStream();
        });

        newEventSource.onerror = (error) => {
            console.error('EventSource error:', error);
            closeStream();
        };
    };

    const closeStream = () => {
        if (eventSource) {
            eventSource.close();
            setEventSource(null);
            setIsStreaming(false);
        }
    };

    useEffect(() => {
        setupStream();
        return () => closeStream();
    }, []);

    return (
        <StreamContext.Provider value={{
            currentResponse,
            isStreaming,
            setupStream,
            closeStream,
        }}>
            {children}
        </StreamContext.Provider>
    );
}

export { StreamProvider, useStream }; 