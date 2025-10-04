import React, { useEffect, useState } from 'react';
import './CrisisToast.css';

interface CrisisToastProps {
  show: boolean;
  reason?: string;
  onClose: () => void;
}

const CrisisToast: React.FC<CrisisToastProps> = ({ show, reason, onClose }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setIsVisible(true);
      // Auto-hide after 8 seconds
      const timer = setTimeout(() => {
        handleClose();
      }, 8000);
      
      return () => clearTimeout(timer);
    } else {
      setIsVisible(false);
    }
  }, [show]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => onClose(), 300); // Wait for fade out animation
  };

  if (!show && !isVisible) return null;

  return (
    <div 
      className={`crisis-toast ${isVisible ? 'show' : ''} ${!show ? 'hide' : ''}`}
      onClick={handleClose}
    >
      <div className="toast-content">
        <div className="toast-icon">🚨</div>
        <div className="toast-text">
          <div className="toast-title">Red Flag! Human Chatter Needed</div>
          <div className="toast-subtitle">
            {reason?.includes('extreme sadness') && 'Crisis situation detected - user needs support'}
            {reason?.includes('mental health') && 'Serious mental health concern detected'}
            {reason?.includes('grief') && 'Grief/Trauma detection - user needs empathy'}
            {reason?.includes('Violent threat') && 'Violent threat detected - immediate human intervention needed'}
            {reason?.includes('violence') && 'Violence concern detected - safety intervention required'}
            {reason?.includes('safety concern') && 'Safety concern detected - human oversight needed'}
            {!reason?.includes('extreme sadness') && !reason?.includes('mental health') && !reason?.includes('grief') && !reason?.includes('Violent threat') && !reason?.includes('violence') && !reason?.includes('safety concern') && 'Critical emotional distress detected'}
          </div>
        </div>
        <button className="toast-close" onClick={handleClose}>
          ✕
        </button>
      </div>
    </div>
  );
};

export default CrisisToast;
