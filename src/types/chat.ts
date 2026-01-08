export interface Source {
  file: string;
  row_index: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: Date;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  sources: Source[];
}

export interface ChatRequest {
  session_id?: string;
  message: string;
  top_k?: number;
}
