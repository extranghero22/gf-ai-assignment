// Chat message component
import React from 'react';
import { Message, EnergyFlags } from '../types';

interface ChatMessageProps {
  message: Message;
  energyFlags?: EnergyFlags;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, energyFlags }) => {
  const isUser = message.role === 'user';
  const timestamp = new Date(message.timestamp * 1000).toLocaleTimeString();

  const getEnergyEmoji = (status: string) => {
    switch (status) {
      case 'green': return '🟢';
      case 'yellow': return '🟡';
      case 'red': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <div className={`message ${isUser ? 'user-message' : 'agent-message'}`}>
      <div className="message-header">
        <span className="message-role">
          {isUser ? 'You' : 'AI Girlfriend'}
        </span>
        <span className="message-time">{timestamp}</span>
        {energyFlags && (
          <span className="energy-indicator" title={energyFlags.reason}>
            {getEnergyEmoji(energyFlags.status)}
          </span>
        )}
      </div>
      <div className="message-content">
        {message.content}
      </div>
      {message.energy_metadata && (
        <div className="energy-metadata">
          <small>
            Energy: {message.energy_metadata.expected_energy || 'Unknown'}
          </small>
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
