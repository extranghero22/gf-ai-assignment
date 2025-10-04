// Session controls component
import React from 'react';

interface SessionControlsProps {
  isActive: boolean;
  onStart: () => void;
  onStop: () => void;
  onGetMetrics: () => void;
  sessionId?: string;
}

const SessionControls: React.FC<SessionControlsProps> = ({
  isActive,
  onStart,
  onStop,
  onGetMetrics,
  sessionId
}) => {
  return (
    <div className="session-controls">
      <div className="session-info">
        <span className={`session-status ${isActive ? 'active' : 'inactive'}`}>
          {isActive ? '🟢 Active' : '🔴 Inactive'}
        </span>
      </div>
      
      <div className="control-buttons">
        {!isActive ? (
          <button 
            onClick={onStart}
            className="btn btn-primary"
          >
            🚀 Start Conversation
          </button>
        ) : (
          <>
            <button 
              onClick={onStop}
              className="btn btn-danger"
            >
              🛑 Stop Chat
            </button>
            <button 
              onClick={onGetMetrics}
              className="btn btn-secondary"
            >
              📊 Metrics
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default SessionControls;
