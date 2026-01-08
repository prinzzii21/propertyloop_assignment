import { useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { ChatHeader } from './ChatHeader';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { EmptyState } from './EmptyState';
import { TypingIndicator } from './TypingIndicator';

export function ChatContainer() {
  const { messages, isLoading, sessionId, sendMessage, clearChat } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto p-4 gap-4">
      <ChatHeader sessionId={sessionId} onClear={clearChat} />
      
      <div className="flex-1 overflow-y-auto rounded-2xl">
        {messages.length === 0 ? (
          <EmptyState onSuggestionClick={sendMessage} />
        ) : (
          <div className="space-y-4 p-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      <ChatInput onSend={sendMessage} isLoading={isLoading} />
    </div>
  );
}
