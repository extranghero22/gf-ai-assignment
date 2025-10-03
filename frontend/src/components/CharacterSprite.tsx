import React, { useState, useEffect } from 'react';
import { EnergyFlags } from '../types';
import './CharacterSprite.css';

interface CharacterSpriteProps {
  energyFlags?: EnergyFlags;
  isTyping?: boolean;
  isActive?: boolean;
  messageCount?: number; // Track total messages to determine progression
}

type OutfitType = 'casual' | 'casual_pullshirt' | 'casual_both' | 'comfy' | 'date' | 'overcoat_buttoned' | 'overcoat_open_topless' | 'overcoat_nude';
type ExpressionType = 'neutral' | 'happy' | 'smirk' | 'wink' | 'closed' | 'pout';

const CharacterSprite: React.FC<CharacterSpriteProps> = ({ 
  energyFlags, 
  isTyping = false,
  isActive = false,
  messageCount = 0
}) => {
  const [currentOutfit, setCurrentOutfit] = useState<OutfitType>('casual');
  const [currentExpression, setCurrentExpression] = useState<ExpressionType>('neutral');
  const [showBlush, setShowBlush] = useState(false);
  const [sexualMessageCount, setSexualMessageCount] = useState(0); // Track sexual script messages
  const [lastMessageCount, setLastMessageCount] = useState(0);
  const [scriptType, setScriptType] = useState<string>(''); // Track script type (room, exhibitionism)

  // Determine outfit based on energy intensity and type
  useEffect(() => {
    if (!isActive) {
      setCurrentOutfit('casual');
      setCurrentExpression('neutral');
      setShowBlush(false);
      setSexualMessageCount(0);
      setLastMessageCount(0);
      setScriptType('');
      return;
    }

    if (energyFlags) {
      const { status, reason } = energyFlags;
      
      // Detect script type from reason (backend sends this info)
      if (reason && reason.toLowerCase().includes('exhibitionism')) {
        setScriptType('exhibitionism');
      } else if (reason && reason.toLowerCase().includes('room')) {
        setScriptType('room');
      }
      
      // Track sexual intensity progression based on message count
      if (status === 'sexual') {
        // Don't change outfit if still awaiting location choice
        if (reason && reason.toLowerCase().includes('awaiting')) {
          console.log('Awaiting location choice - keeping current outfit');
          // Don't increment count or change outfit yet
        } else {
          // Increment count when new messages arrive
          if (messageCount > lastMessageCount) {
            setSexualMessageCount(prev => prev + 1);
            setLastMessageCount(messageCount);
            console.log(`Sexual script progression: ${sexualMessageCount + 1}/10, Type: ${scriptType}`);
          }
        }
        
        // Check if this is exhibitionism script (overcoat outfit - NO ANIMATION)
        // 3-stage progression: buttoned → open topless → fully nude
        if (scriptType === 'exhibitionism' || (reason && reason.toLowerCase().includes('public')) || (reason && reason.toLowerCase().includes('outside'))) {
          // STATIC ONLY: Progressive reveal in 3 stages
          if (sexualMessageCount >= 7) {
            console.log(`🔥🔥 EXHIBIT SCRIPT: Message ${sexualMessageCount + 1} → FULLY NUDE`);
            setCurrentOutfit('overcoat_nude'); // Stage 3: Fully exposed
          } else if (sexualMessageCount >= 4) {
            console.log(`🔥 EXHIBIT SCRIPT: Message ${sexualMessageCount + 1} → OPEN COAT TOPLESS`);
            setCurrentOutfit('overcoat_open_topless'); // Stage 2: Coat open, topless
          } else {
            console.log(`🔒 EXHIBIT SCRIPT: Message ${sexualMessageCount + 1} → BUTTONED COAT`);
            setCurrentOutfit('overcoat_buttoned'); // Stage 1: Fully covered
          }
        } else {
          // Room script (casual wear)
          // Progressive outfit reveal based on sexual message count (10 message script)
          // Messages 1-5: pullshirt, Messages 6+: both revealed
          if (sexualMessageCount >= 6) {
            console.log('Setting outfit to: casual_both (fully revealed)');
            setCurrentOutfit('casual_both'); // Both revealed (deeper into script)
          } else if (sexualMessageCount >= 1) {
            console.log('Setting outfit to: casual_pullshirt (shirt pulled)');
            setCurrentOutfit('casual_pullshirt'); // Start with shirt pulled
          } else {
            setCurrentOutfit('casual');
          }
        }
      } else         if (status === 'casual') {
          setCurrentOutfit('casual');
          if (sexualMessageCount > 0) {
            setSexualMessageCount(0);
            setScriptType('');
          }
        } else {
          // Reset to casual for non-sexual states
          if (sexualMessageCount > 0) {
            setSexualMessageCount(0);
            setCurrentOutfit('casual');
            setScriptType('');
          }
        }
    }
  }, [energyFlags, isActive, messageCount, sexualMessageCount, lastMessageCount, scriptType]);

  // Animation removed - using static images only

  // Determine expression based on energy type and level
  useEffect(() => {
    if (!isActive) {
      setCurrentExpression('neutral');
      setShowBlush(false);
      return;
    }

    if (energyFlags) {
      const { status, reason } = energyFlags;
      
      // Set blush for intimate/sexual content
      if (status === 'sexual' || reason?.toLowerCase().includes('intimate')) {
        setShowBlush(true);
        
        // Cycle through flirty expressions
        const flirtyExpressions: ExpressionType[] = ['smirk', 'wink', 'happy'];
        const randomExpr = flirtyExpressions[Math.floor(Math.random() * flirtyExpressions.length)];
        setCurrentExpression(randomExpr);
      } else if (status === 'teasing') {
        // Teasing mode: playful expressions without blush
        setShowBlush(false);
        const teasingExpressions: ExpressionType[] = ['smirk', 'wink', 'happy'];
        const randomExpr = teasingExpressions[Math.floor(Math.random() * teasingExpressions.length)];
        setCurrentExpression(randomExpr);
      } else if (status === 'casual') {
        setShowBlush(false);
        setCurrentExpression('happy');
      } else if (status === 'red') {
        setShowBlush(false);
        setCurrentExpression('neutral');
      } else if (status === 'yellow') {
        setShowBlush(false);
        setCurrentExpression('neutral');
      } else {
        setShowBlush(false);
        setCurrentExpression('happy');
      }
    }
    
    // When typing, occasionally wink or smile
    if (isTyping) {
      const typingExpressions: ExpressionType[] = ['happy', 'smirk', 'neutral'];
      const randomExpr = typingExpressions[Math.floor(Math.random() * typingExpressions.length)];
      setCurrentExpression(randomExpr);
    }
  }, [energyFlags, isTyping, isActive]);

  // Get outfit image path
  const getOutfitPath = () => {
    const basePath = '/images/Incoatnito/7 idle standing outfits/fullbody';
    
    switch (currentOutfit) {
      case 'casual':
        return `${basePath}/Casual Wear/base.png`;
      case 'casual_pullshirt':
        return `${basePath}/Casual Wear/pullshirt.png`;
      case 'casual_both':
        return `${basePath}/Casual Wear/both.png`;
      case 'comfy':
        return `${basePath}/Comfy 1.png`;
      case 'date':
        return `${basePath}/Date Wear/base.png`;
      case 'overcoat_buttoned':
        // Stage 1: Buttoned coat - fully covered
        const buttonedPath = `${basePath}/Overcoat/buttoned_coat.png`;
        console.log(`🔒 LOADING BUTTONED COAT: ${buttonedPath}`);
        return buttonedPath;
      case 'overcoat_open_topless':
        // Stage 2: Open coat, topless underneath
        console.log(`🔥 LOADING OPEN COAT TOPLESS`);
        return `${basePath}/Overcoat/open_coat_topless.png`;
      case 'overcoat_nude':
        // Stage 3: Fully nude/exposed
        console.log(`🔥🔥 LOADING FULLY NUDE`);
        return `${basePath}/Casual Wear/both.png`; // Use fully exposed casual outfit
      default:
        return `${basePath}/Casual Wear/base.png`;
    }
  };

  // Get expression overlay paths
  const getExpressionPaths = () => {
    const basePath = '/images/Incoatnito/7 idle standing outfits/overlays/expressions';
    
    let eyesPath = `${basePath}/eyes_open.png`;
    let mouthPath = `${basePath}/mouth_closed.png`;
    
    switch (currentExpression) {
      case 'happy':
        eyesPath = `${basePath}/eyes_open.png`;
        mouthPath = `${basePath}/mouth_smile.png`;
        break;
      case 'smirk':
        eyesPath = `${basePath}/eyes_open.png`;
        mouthPath = `${basePath}/mouth_smirk.png`;
        break;
      case 'wink':
        eyesPath = `${basePath}/eyes_wink.png`;
        mouthPath = `${basePath}/mouth_smile.png`;
        break;
      case 'closed':
        eyesPath = `${basePath}/eyes_closed.png`;
        mouthPath = `${basePath}/mouth_smile.png`;
        break;
      case 'pout':
        eyesPath = `${basePath}/eyes_open.png`;
        mouthPath = `${basePath}/mouth_pout.png`;
        break;
      case 'neutral':
      default:
        eyesPath = `${basePath}/eyes_open.png`;
        mouthPath = `${basePath}/mouth_closed.png`;
        break;
    }
    
    return { eyesPath, mouthPath };
  };

  const { eyesPath, mouthPath } = getExpressionPaths();
  const blushPath = '/images/Incoatnito/7 idle standing outfits/overlays/expressions/blush.png';

  // Determine background scene based on energy flags
  const getBackgroundScene = () => {
    const scene = energyFlags?.scene;
    
    switch (scene) {
      case 'room':
        return '/images/scenes/room.jpg';
      case 'beach':
        return '/images/scenes/beach.jpg';
      case 'park':
        return '/images/scenes/walkway-garden-bangkok-thailand.jpg';
      default:
        return '/images/scenes/walkway-garden-bangkok-thailand.jpg'; // Default park scene
    }
  };

  // Static images only - no animation

  return (
    <div 
      className={`character-sprite-container ${isActive ? 'active' : 'inactive'}`}
      style={{
        backgroundImage: `url('${getBackgroundScene()}')`
      }}
    >
      <div className="sprite-wrapper">
        {/* Static sprite with normal expressions - NO ANIMATION */}
        <>
            {/* Static sprite with normal expressions */}
            <img 
              src={getOutfitPath()} 
              alt="Character" 
              className="sprite-layer sprite-base"
            />
            
            {/* Eyes overlay */}
            <img 
              src={eyesPath} 
              alt="Eyes" 
              className="sprite-layer sprite-expression"
            />
            
            {/* Mouth overlay */}
            <img 
              src={mouthPath} 
              alt="Mouth" 
              className="sprite-layer sprite-expression"
            />
            
            {/* Blush overlay (conditional) */}
            {showBlush && (
              <img 
                src={blushPath} 
                alt="Blush" 
                className="sprite-layer sprite-blush"
              />
            )}
        </>
        
        {/* Typing indicator overlay */}
        {isTyping && (
          <div className="sprite-typing-indicator">
            <div className="typing-bubble">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
      </div>
      
      <div className="sprite-name">
        <span className="name-text">Linh</span>
        <span className="mood-text">
          {!isActive && 'Waiting for you...'}
          {isActive && energyFlags && energyFlags.status === 'sexual' && 'Feeling intimate...'}
          {isActive && energyFlags && energyFlags.status === 'teasing' && 'Playfully teasing...'}
          {isActive && energyFlags && energyFlags.status === 'casual' && 'Chatting casually'}
          {isActive && energyFlags && energyFlags.status === 'yellow' && 'A bit concerned'}
          {isActive && energyFlags && energyFlags.status === 'red' && 'Very concerned'}
          {isActive && energyFlags && energyFlags.status === 'green' && 'Happy to chat'}
        </span>
      </div>
    </div>
  );
};

export default CharacterSprite;

