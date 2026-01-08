import { Bot } from 'lucide-react';

export function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary border border-border flex items-center justify-center">
        <Bot className="h-4 w-4" />
      </div>
      
      <div className="chat-bubble-assistant px-4 py-3">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-pulse-soft" style={{ animationDelay: '0ms' }} />
          <span className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-pulse-soft" style={{ animationDelay: '200ms' }} />
          <span className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-pulse-soft" style={{ animationDelay: '400ms' }} />
        </div>
      </div>
    </div>
  );
}
