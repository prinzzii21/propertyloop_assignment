import { BarChart3, TrendingUp, PieChart, Search } from 'lucide-react';

const suggestions = [
  {
    icon: BarChart3,
    text: "What are my top 5 holdings by value?",
  },
  {
    icon: TrendingUp,
    text: "Show total PnL from recent trades",
  },
  {
    icon: PieChart,
    text: "What's my net position in AAPL?",
  },
  {
    icon: Search,
    text: "Find all trades over $10,000",
  },
];

interface EmptyStateProps {
  onSuggestionClick: (text: string) => void;
}

export function EmptyState({ onSuggestionClick }: EmptyStateProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 animate-fade-in">
      <div className="h-16 w-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6">
        <BarChart3 className="h-8 w-8 text-primary" />
      </div>
      
      <h2 className="text-xl font-semibold text-foreground mb-2">
        Ask about your financial data
      </h2>
      <p className="text-sm text-muted-foreground text-center max-w-md mb-8">
        I can analyze your holdings and trades data. Ask questions about positions, 
        calculate totals, find specific transactions, or get insights.
      </p>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
        {suggestions.map((suggestion, idx) => (
          <button
            key={idx}
            onClick={() => onSuggestionClick(suggestion.text)}
            className="flex items-center gap-3 p-3 rounded-xl bg-card border border-border
                       hover:bg-secondary hover:border-primary/20 transition-all text-left group"
          >
            <div className="h-8 w-8 rounded-lg bg-secondary group-hover:bg-primary/10 
                          flex items-center justify-center transition-colors">
              <suggestion.icon className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
            </div>
            <span className="text-sm text-foreground">{suggestion.text}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
