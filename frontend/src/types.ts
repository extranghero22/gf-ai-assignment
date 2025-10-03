// Types for the conversation system

export interface EnergySignature {
  timestamp: number;
  energy_level: string;
  energy_type: string;
  dominant_emotion: string;
  nervous_system_state: string;
  intensity_score: number;
  confidence: number;
}

export interface Message {
  role: 'user' | 'agent';
  content: string;
  timestamp: number;
  energy_metadata?: any;
  session_index?: number;
}

export interface EnergyFlags {
  status: 'green' | 'yellow' | 'red' | 'sexual' | 'casual' | 'teasing';
  reason: string;
}

export interface ApiResponse {
  status: string;
  ai_response?: string;
  energy_status?: EnergyFlags;
  error?: string;
}

export interface SessionInfo {
  status: string;
  session_id?: string;
  error?: string;
}
