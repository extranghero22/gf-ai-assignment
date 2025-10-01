// Metrics modal component
import React from 'react';

interface MetricsModalProps {
  isOpen: boolean;
  onClose: () => void;
  metrics: any;
}

const MetricsModal: React.FC<MetricsModalProps> = ({ isOpen, onClose, metrics }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>📊 Session Metrics</h2>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>
        
        <div className="modal-body">
          {metrics ? (
            <div className="metrics-grid">
              <div className="metric-item">
                <label>Session ID:</label>
                <span>{metrics.session_id}</span>
              </div>
              
              <div className="metric-item">
                <label>Duration:</label>
                <span>{Math.round(metrics.duration || 0)}s</span>
              </div>
              
              <div className="metric-item">
                <label>Messages:</label>
                <span>{metrics.message_count || 0}</span>
              </div>
              
              <div className="metric-item">
                <label>Energy Alerts:</label>
                <span>{metrics.energy_alerts || 0}</span>
              </div>
              
              <div className="metric-item">
                <label>Safety Incidents:</label>
                <span>{metrics.safety_incidents || 0}</span>
              </div>
              
              <div className="metric-item">
                <label>Avg Energy Intensity:</label>
                <span>{(metrics.avg_energy_intensity || 0).toFixed(2)}</span>
              </div>
              
              {metrics.energy_trends && (
                <div className="metric-item">
                  <label>Energy Trend:</label>
                  <span>{metrics.energy_trends.trend}</span>
                </div>
              )}
              
              {metrics.dominant_emotions && Object.keys(metrics.dominant_emotions).length > 0 && (
                <div className="metric-item full-width">
                  <label>Dominant Emotions:</label>
                  <div className="emotion-list">
                    {Object.entries(metrics.dominant_emotions).map(([emotion, count]) => (
                      <span key={emotion} className="emotion-tag">
                        {`${emotion}: ${count}`}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p>No metrics available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default MetricsModal;
