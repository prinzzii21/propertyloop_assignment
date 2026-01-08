import { useState, useCallback } from 'react';
import { Message, ChatResponse, Source } from '@/types/chat';

const API_URL = 'http://localhost:8000';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string, topK: number = 5) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: content.trim(),
          top_k: topK,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      
      setSessionId(data.session_id);
      
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      
      // Add error message to chat
      const errorResponse: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `⚠️ ${errorMessage}. Make sure the backend is running at ${API_URL}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sessionId,
    sendMessage,
    clearChat,
  };
}
