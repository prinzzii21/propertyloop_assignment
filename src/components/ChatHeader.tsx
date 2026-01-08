import { Database, Trash2, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface ChatHeaderProps {
  sessionId: string | null;
  onClear: () => void;
}

export function ChatHeader({ sessionId, onClear }: ChatHeaderProps) {
  return (
    <header className="glass-panel rounded-2xl p-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center">
          <Database className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h1 className="font-semibold text-foreground">Financial Data Assistant</h1>
          <p className="text-xs text-muted-foreground">
            {sessionId ? (
              <span>Session: {sessionId.slice(0, 8)}...</span>
            ) : (
              <span>Ask questions about holdings & trades</span>
            )}
          </p>
        </div>
      </div>
      
      <div className="flex items-center gap-1">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button 
              variant="ghost" 
              size="icon" 
              className="h-9 w-9 rounded-xl"
              onClick={onClear}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Clear chat</TooltipContent>
        </Tooltip>
      </div>
    </header>
  );
}
