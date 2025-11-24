"""
Routing path types - separated to avoid circular imports
"""

from enum import Enum


class RoutingPath(Enum):
    """Response routing paths"""
    RESPOND_NORMALLY = "PATH_A"           # Straightforward, on-topic, appropriate
    RESPOND_WITH_CONFUSION = "PATH_B"     # Complex/deep topics, act confused
    DEFLECT_REDIRECT = "PATH_C"           # Uncomfortable, boring, redirect
    MINIMAL_RESPONSE = "PATH_D"           # Doesn't require much, create tension
    IGNORE_SELF_FOCUS = "PATH_E"          # Redirect to ourselves, be dramatic
    EMOTIONAL_REACTION = "PATH_F"         # Strong emotion, be expressive
    JEALOUS_POSSESSIVE = "PATH_G"         # Other people mentioned romantically
    PLAYFUL_TEASE = "PATH_I"              # Opportunity to playfully challenge
    VULNERABLE_REASSURANCE = "PATH_L"     # Show insecurity, seek validation
    BOUNDARY_FIRM = "PATH_M"              # Firmly maintain boundaries
