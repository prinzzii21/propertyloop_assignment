import { Message, Source } from '@/types/chat';
import { User, Bot, FileSpreadsheet } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatMessageProps {
  message: Message;
}

function SourceBadge({ source }: { source: Source }) {
  const fileName = source.file.replace('.csv', '');
  const isHoldings = fileName === 'holdings';
  
  return (
    <span className="source-badge">
      <FileSpreadsheet className="h-3 w-3" />
      <span className={cn(
        "font-medium",
        isHoldings ? "text-primary" : "text-accent-foreground"
      )}>
        {fileName}
      </span>
      <span className="text-muted-foreground">row {source.row_index}</span>
    </span>
  );
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  
  return (
    <div className={cn(
      "flex gap-3 animate-slide-up",
      isUser ? "flex-row-reverse" : "flex-row"
    )}>
      {/* Avatar */}
      <div className={cn(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
        isUser 
          ? "bg-primary text-primary-foreground" 
          : "bg-secondary border border-border"
      )}>
        {isUser ? (
          <User className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </div>
      
      {/* Message Content */}
      <div className={cn(
        "max-w-[80%] px-4 py-3",
        isUser ? "chat-bubble-user" : "chat-bubble-assistant"
      )}>
        <p className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </p>
        
        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-border/50">
            <p className="text-xs text-muted-foreground mb-2">Sources:</p>
            <div className="flex flex-wrap gap-2">
              {message.sources.map((source, idx) => (
                <SourceBadge key={idx} source={source} />
              ))}
            </div>
          </div>
        )}
        
        {/* Timestamp */}
        <p className={cn(
          "text-xs mt-2",
          isUser ? "text-primary-foreground/70" : "text-muted-foreground"
        )}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
}
