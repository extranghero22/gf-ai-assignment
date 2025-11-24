// Main App component
import React, { useState, useRef, useEffect } from 'react';
import { Message, EnergyFlags, ApiResponse } from './types';
import { conversationApi, StreamMessagePart, StreamComplete, StreamError, GhostMessage } from './services/api';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import EnergyIndicator from './components/EnergyIndicator';
import SessionControls from './components/SessionControls';
import MetricsModal from './components/MetricsModal';
import CharacterSprite from './components/CharacterSprite';
import CrisisToast from './components/CrisisToast';
import './App.css';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isActive, setIsActive] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [currentEnergyFlags, setCurrentEnergyFlags] = useState<EnergyFlags | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showMetrics, setShowMetrics] = useState(false);
  const [showCrisisToast, setShowCrisisToast] = useState(false);
  const [crisisToastReason, setCrisisToastReason] = useState<string>('');
  const [metrics, setMetrics] = useState<any>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<string>('');
  const [isTyping, setIsTyping] = useState(false);
  const [pendingMessages, setPendingMessages] = useState<string[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Effect to handle pending messages with typing simulation
  useEffect(() => {
    if (pendingMessages.length > 0) {
      let currentIndex = 0;

      const showNextMessage = () => {
        if (currentIndex < pendingMessages.length) {
          const message = pendingMessages[currentIndex];

          // Add the message to the chat
          const newMessage: Message = {
            role: 'agent',
            content: message,
            timestamp: Date.now() / 1000,
          };
          setMessages(prev => [...prev, newMessage]);

          currentIndex++;

          // If there are more messages, continue typing
          if (currentIndex < pendingMessages.length) {
            setTimeout(showNextMessage, 1500 + Math.random() * 1000); // 1.5-2.5 second delay
          } else {
            setIsTyping(false);
            setPendingMessages([]); // Clear pending messages
          }
        }
      };

      // Start showing messages after a brief delay
      setTimeout(showNextMessage, 800 + Math.random() * 700); // 0.8-1.5 second initial delay
    }
  }, [pendingMessages.length]); // Only depend on length, not the array itself

  // Effect to poll for ghost messages (auto-messages when user is inactive)
  useEffect(() => {
    if (!isActive || isStreaming || isTyping) {
      return; // Don't poll if session not active or currently streaming/typing
    }

    const pollInterval = setInterval(async () => {
      try {
        const response = await conversationApi.pollMessages();

        if (response.messages && response.messages.length > 0) {
          // Add ghost messages to the chat
          response.messages.forEach((ghostMsg: GhostMessage) => {
            const newMessage: Message = {
              role: 'agent',
              content: ghostMsg.content,
              timestamp: ghostMsg.timestamp,
            };
            setMessages(prev => [...prev, newMessage]);
            console.log('Ghost message received:', ghostMsg.content);
          });
        }
      } catch (error) {
        // Silently ignore poll errors to avoid spam
        console.debug('Poll error:', error);
      }
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(pollInterval);
  }, [isActive, isStreaming, isTyping]);

  const startConversation = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await conversationApi.startConversation();
      
      if (response.error) {
        setError(response.error);
        return;
      }
      
      setIsActive(true);
      setSessionId(response.session_id);
      setMessages([]);
      
      // Add welcome message
      const welcomeMessage: Message = {
        role: 'agent',
        content: 'Hey baby! I\'m here and ready to chat with you. What\'s on your mind? 💕',
        timestamp: Date.now() / 1000,
      };
      setMessages([welcomeMessage]);
      
    } catch (error) {
      console.error('Error starting conversation:', error);
      setError('Failed to start conversation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const stopConversation = async () => {
    try {
      setIsLoading(true);
      await conversationApi.stopConversation();
      setIsActive(false);
      setSessionId(undefined);
      setCurrentEnergyFlags(undefined);
    } catch (error) {
      console.error('Error stopping conversation:', error);
      setError('Failed to stop conversation.');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (content: string) => {
    if (!isActive) return;

    // Add user message immediately
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: Date.now() / 1000,
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      setIsStreaming(true);
      setCurrentStreamingMessage('');
      setIsTyping(true);
      setPendingMessages([]);
      setError(null);

      // Use streaming API for multi-message typing simulation
      console.log('Starting streaming request...');
      let collectedMessages: string[] = [];
      
      await conversationApi.sendMessageStream(
        content,
        // onMessagePart
        (part: StreamMessagePart) => {
          console.log('Received message part:', part);
          if (part.is_typing) {
            // Show typing indicator
            console.log('Setting typing indicator:', part.content);
            setCurrentStreamingMessage(part.content);
          } else {
            // Filter out standalone punctuation and typing indicators (but allow full messages)
            const content = part.content.trim();
            const isTypingIndicator = (content === '.' || content === '..' || content === '...' || 
                                     content === 'typing...' || content === 'one sec...' || 
                                     content === 'let me think...' || content === 'um' || content === 'well' || content === 'so') &&
                                     content.length < 20; // Only filter if it's a short standalone indicator
            
            if (!isTypingIndicator && content.length > 0) {
              // Collect message parts for delayed display
              console.log('Collecting message part:', part.content);
              collectedMessages.push(part.content);
            } else {
              console.log('Filtered out typing indicator:', part.content);
            }
          }
        },
        // onComplete
        (complete: StreamComplete) => {
          console.log('Stream completed:', complete);
          
          // Update energy flags
          if (complete.energy_status) {
            setCurrentEnergyFlags(complete.energy_status);
            
            // Check for crisis situation and show alert
            if (complete.energy_status.status === 'red' && 
                (complete.energy_status.reason.includes('crisis') || 
                 complete.energy_status.reason.includes('mental health') ||
                 complete.energy_status.reason.includes('extreme sadness') ||
                 complete.energy_status.reason.includes('Violent threat') ||
                 complete.energy_status.reason.includes('violence') ||
                 complete.energy_status.reason.includes('safety concern'))) {
              setCrisisToastReason(complete.energy_status.reason);
              setShowCrisisToast(true);
            }
          }
          
          // Check if session was stopped due to safety concerns
          if ((complete as any).session_stopped) {
            console.log('Session stopped due to safety concerns - stopping chat automatically');
            setIsActive(false);
            setSessionId(undefined);
            setCrisisToastReason('Session terminated due to safety concerns');
            setShowCrisisToast(true);
          }
          
          // Start the typing simulation with collected messages
          if (collectedMessages.length > 0) {
            console.log('Starting typing simulation with messages:', collectedMessages);
            setPendingMessages(collectedMessages);
          } else {
            setIsTyping(false);
          }
          
          setIsStreaming(false);
          setCurrentStreamingMessage('');
        },
        // onError
        (error: StreamError) => {
          console.error('Stream error:', error);
          setError(error.message);
          setIsStreaming(false);
          setCurrentStreamingMessage('');
          setIsTyping(false);
          setPendingMessages([]);
        }
      );

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Check if session was stopped due to safety concerns
      if (error instanceof Error && error.message.includes('Session has been stopped')) {
        setCrisisToastReason('Session terminated due to safety concerns');
        setShowCrisisToast(true);
        setError('Session terminated due to safety concerns. Please start a new conversation.');
      } else {
        setError('Failed to send message. Please try again.');
      }
      
      setIsStreaming(false);
      setCurrentStreamingMessage('');
    }
  };

  const getMetrics = async () => {
    try {
      const metricsData = await conversationApi.getMetrics();
      setMetrics(metricsData);
      setShowMetrics(true);
    } catch (error) {
      console.error('Error getting metrics:', error);
      setError('Failed to get metrics.');
    }
  };

  const resetApplication = () => {
    // Refresh the entire page to reset everything
    window.location.reload();
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1> Date Linh </h1>
        <p>AI Chat with Linh</p>
      </header>

      <main className="app-main">
        {/* Character Sprite Section */}
        <CharacterSprite 
          energyFlags={currentEnergyFlags}
          isTyping={isTyping}
          isActive={isActive}
          messageCount={messages.length}
        />

        <div className="chat-container">
          <div className="chat-header">
            <SessionControls
              isActive={isActive}
              onStart={startConversation}
              onStop={stopConversation}
              onGetMetrics={getMetrics}
              onReset={resetApplication}
              sessionId={sessionId}
              hasMessages={messages.length > 0}
            />
            
            {currentEnergyFlags && (
              <EnergyIndicator 
                energyFlags={currentEnergyFlags} 
                showDetails={true}
              />
            )}
          </div>

          <div className="chat-messages">
            {messages.map((message, index) => (
              <ChatMessage
                key={index}
                message={message}
                energyFlags={index === messages.length - 1 ? currentEnergyFlags : undefined}
              />
            ))}
            
            {isTyping && (
              <div className="message agent-message">
                <div className="message-header">
                  <span className="message-role">AI Girlfriend</span>
                  <span className="message-time">{new Date().toLocaleTimeString()}</span>
                </div>
                <div className="message-content typing-indicator-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span className="typing-text">typing...</span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {error && (
            <div className="error-message">
              <span>⚠️ {error}</span>
              <button onClick={() => setError(null)}>✕</button>
            </div>
          )}

          {/* Crisis Alert Toast */}
          <CrisisToast 
            show={showCrisisToast}
            reason={crisisToastReason}
            onClose={() => {
              setShowCrisisToast(false);
              setCrisisToastReason('');
            }}
          />

          <div className="chat-input-container">
            <ChatInput
              onSendMessage={sendMessage}
              disabled={!isActive || isStreaming}
              placeholder={isActive ? "Type your message..." : "Start a conversation to begin chatting"}
            />
          </div>
        </div>
      </main>

      <MetricsModal
        isOpen={showMetrics}
        onClose={() => setShowMetrics(false)}
        metrics={metrics}
      />
    </div>
  );
};

export default App;