// API service for communicating with the backend
import axios from 'axios';
import { ApiResponse, SessionInfo } from '../types';

// Types for streaming responses
export interface StreamMessagePart {
  type: 'message_part';
  content: string;
  index: number;
  total: number;
  is_typing: boolean;
}

export interface StreamComplete {
  type: 'complete';
  energy_status: any;
  session_stopped?: boolean;
}

export interface StreamError {
  type: 'error';
  message: string;
}

export type StreamEvent = StreamMessagePart | StreamComplete | StreamError;

// Check if we're in production (deployed) or development
const isProduction = process.env.NODE_ENV === 'production';
// Replace this with your actual Railway backend URL after deployment
const API_BASE_URL = isProduction ? 'https://your-backend-url.railway.app/api' : 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Note: Mock responses removed - now using real backend API

export const conversationApi = {
  // Start a new conversation session
  startConversation: async (): Promise<SessionInfo> => {
    try {
      const response = await api.post('/start');
      return response.data;
    } catch (error) {
      console.error('Error starting conversation:', error);
      throw error;
    }
  },

  // Send a message to the conversation
  sendMessage: async (message: string): Promise<ApiResponse> => {
    try {
      const response = await api.post('/send', { message });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  // Send a message with streaming response
  sendMessageStream: async (
    message: string,
    onMessagePart: (part: StreamMessagePart) => void,
    onComplete: (complete: StreamComplete) => void,
    onError: (error: StreamError) => void
  ): Promise<void> => {
    try {
      console.log('Sending streaming request to:', `${API_BASE_URL}/send-stream`);
      console.log('Message:', message);
      
      const response = await fetch(`${API_BASE_URL}/send-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body reader available');
      }

      console.log('Starting to read stream...');
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log('Stream reading completed');
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        console.log('Received chunk:', chunk);
        buffer += chunk;
        
        // Process complete lines
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          console.log('Processing line:', line);
          if (line.startsWith('data: ')) {
            try {
              const jsonData = line.slice(6);
              console.log('JSON data:', jsonData);
              const data = JSON.parse(jsonData);
              const event = data as StreamEvent;
              console.log('Parsed event:', event);
              
              switch (event.type) {
                case 'message_part':
                  console.log('Calling onMessagePart with:', event);
                  onMessagePart(event);
                  break;
                case 'complete':
                  console.log('Calling onComplete with:', event);
                  onComplete(event);
                  break;
                case 'error':
                  console.log('Calling onError with:', event);
                  onError(event);
                  break;
                default:
                  console.log('Unknown event type:', (event as any).type);
              }
            } catch (parseError) {
              console.error('Error parsing stream data:', parseError);
              console.error('Problematic line:', line);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error in streaming request:', error);
      onError({
        type: 'error',
        message: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  },

  // Stop the current conversation
  stopConversation: async (): Promise<{ status: string }> => {
    try {
      const response = await api.post('/stop');
      return response.data;
    } catch (error) {
      console.error('Error stopping conversation:', error);
      throw error;
    }
  },

  // Get conversation metrics
  getMetrics: async (): Promise<any> => {
    try {
      const response = await api.get('/metrics');
      return response.data;
    } catch (error) {
      console.error('Error getting metrics:', error);
      throw error;
    }
  },
};
