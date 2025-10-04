"""
Test that the CURIOUS emotion state is now valid
"""

from energy_types import EmotionState
from enhanced_agents import EmotionState as EnhancedEmotionState

def test_curious_emotion():
    """Test that curiosity is now a valid emotion state"""
    
    print("Testing CURIOUS Emotion State Addition")
    print("=" * 45)
    
    # Test the main emotion enum
    print("Testing energy_types.py EmotionState:")
    try:
        curious_emotion = EmotionState.CURIOUS
        print(f"OK CURIOUS = '{curious_emotion.value}'")
    except AttributeError as e:
        print(f"ERROR accessing EmotionState.CURIOUS: {e}")
    
    # Test all available emotions
    print("\nAll EmotionState values:")
    for emotion in EmotionState:
        print(f"  {emotion.name:12} = '{emotion.value}'")
    
    print(f"\nTotal emotions: {len(EmotionState)}")
    
    # Test the enhanced agents enum
    print("\nTesting enhanced_agents.py EmotionState:")
    try:
        enhanced_curious = EnhancedEmotionState.CURIOUS
        print(f"OK Enhanced CURIOUS = '{enhanced_curious.value}'")
    except AttributeError as e:
        print(f"ERROR accessing EnhancedEmotionState.CURIOUS: {e}")
    
    # Test that both enums have the same values
    print("\nComparing emotion counts:")
    print(f"  energy_types: {len(EmotionState)} emotions")
    print(f"  enhanced_agents: {len(EnhancedEmotionState)} emotions")
    
    if len(EmotionState) == len(EnhancedEmotionState):
        print("OK Both enums have the same number of emotions")
    else:
        print("ERROR Emotion count mismatch!")

def test_enum_compatibility():
    """Test enum compatibility and value access"""
    
    print("\nTesting Enum Compatibility")
    print("=" * 30)
    
    # Test creating energy signatures with CURIOUS
    from energy_types import EnergySignature, EnergyLevel, EnergyType, NervousSystemState
    import time
    
    print("Creating EnergySignature with CURIOUS emotion:")
    try:
        test_signature = EnergySignature(
            timestamp=time.time(),
            energy_level=EnergyLevel.MEDIUM,
            energy_type=EnergyType.COOPERATIVE,
            dominant_emotion=EmotionState.CURIOUS,
            nervous_system_state=NervousSystemState.REST_AND_DIGEST,
            intensity_score=0.7,
            confidence=0.8
        )
        
        print(f"OK EnergySignature created successfully")
        print(f"  Emotion: {test_signature.dominant_emotion}")
        print(f"  Value: {test_signature.dominant_emotion.value}")
        
    except Exception as e:
        print(f"ERROR creating EnergySignature: {e}")

if __name__ == "__main__":
    test_curious_emotion()
    test_enum_compatibility()
