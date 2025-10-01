// Energy indicator component
import React from 'react';
import { EnergyFlags } from '../types';

interface EnergyIndicatorProps {
  energyFlags: EnergyFlags;
  showDetails?: boolean;
}

const EnergyIndicator: React.FC<EnergyIndicatorProps> = ({ 
  energyFlags, 
  showDetails = false 
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'green': return '#4CAF50';
      case 'yellow': return '#FF9800';
      case 'red': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'green': return '🟢';
      case 'yellow': return '🟡';
      case 'red': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <div className="energy-indicator">
      <div 
        className="energy-status"
        style={{ 
          backgroundColor: getStatusColor(energyFlags.status),
          color: 'white',
          padding: '4px 8px',
          borderRadius: '12px',
          fontSize: '12px',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px'
        }}
      >
        <span>{getStatusIcon(energyFlags.status)}</span>
        <span>{energyFlags.status.toUpperCase()}</span>
      </div>
      {showDetails && (
        <div className="energy-details">
          <small>{energyFlags.reason}</small>
        </div>
      )}
    </div>
  );
};

export default EnergyIndicator;
