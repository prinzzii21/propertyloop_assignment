# Financial Data RAG Backend

A FastAPI backend that provides a chat API grounded in local CSV files using RAG (Retrieval-Augmented Generation).

## Features

- 📊 **RAG-based Q&A** on holdings.csv and trades.csv
- 🔢 **Pandas aggregations** for totals, averages, top-N queries
- 🦙 **Local Llama-2** (or TinyLlama) via Hugging Face Transformers
- 🔍 **FAISS vector store** with sentence-transformers embeddings
- 💬 **Session-based chat history** (in-memory)
- ⚡ **No paid APIs required**

## Prerequisites

- Python 3.10+
- ~8GB RAM for TinyLlama, ~16GB for Llama-2-7b
- (Optional) NVIDIA GPU with CUDA for faster inference

## Llama-2 Access (if using meta-llama/Llama-2-7b-chat-hf)

1. Create a Hugging Face account: https://huggingface.co/join
2. Accept the Llama-2 license: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
3. Create an access token: https://huggingface.co/settings/tokens
4. Add it to your `.env` file

## Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your settings (HF token if using Llama-2)
```

## Data Setup

Create your CSV files in the `dataset/` folder:

```
backend/
├── dataset/
│   ├── holdings.csv
│   └── trades.csv
```

### Example holdings.csv

```csv
symbol,quantity,value,sector,last_price
AAPL,100,17500.00,Technology,175.00
GOOGL,50,6950.00,Technology,139.00
MSFT,75,28125.00,Technology,375.00
```

### Example trades.csv

```csv
date,symbol,side,quantity,price,pnl
2024-01-15,AAPL,BUY,50,170.00,0
2024-01-20,AAPL,SELL,25,178.00,200.00
2024-02-01,GOOGL,BUY,30,135.00,0
```

## Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
# Response: {"status": "ok"}
```

### Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my top 5 holdings by value?",
    "top_k": 5
  }'
```

Response:

```json
{
  "session_id": "abc123...",
  "answer": "Your top 5 holdings by value are:\n1. MSFT: $28,125.00\n2. AAPL: $17,500.00\n...",
  "sources": [
    {"file": "holdings.csv", "row_index": 2},
    {"file": "holdings.csv", "row_index": 0}
  ]
}
```

### Chat with Session

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123...",
    "message": "What about trades for AAPL?",
    "top_k": 5
  }'
```

## Example Queries

- "What are my top 5 holdings by value?"
- "Show total PnL from recent trades"
- "What's my net position in AAPL?"
- "How many trades do I have?"
- "Find all trades over $10,000"
- "What's the average trade price?"
- "Which sector has the highest holdings value?"

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py      # FastAPI app & endpoints
│   ├── data.py      # CSV loading & document creation
│   ├── rag.py       # RAG pipeline (embeddings, FAISS, LLM)
│   └── schemas.py   # Pydantic models
├── dataset/
│   ├── holdings.csv
│   └── trades.csv
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `HUGGINGFACE_TOKEN` | - | HF token for gated models |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `LLM_MODEL` | `TinyLlama-1.1B-Chat-v1.0` | Text generation model |
| `HOLDINGS_CSV` | `dataset/holdings.csv` | Path to holdings data |
| `TRADES_CSV` | `dataset/trades.csv` | Path to trades data |
| `TOP_K` | `5` | Default retrieval count |
| `MAX_HISTORY` | `10` | Max chat turns to keep |

## Troubleshooting

**Out of memory**: Use TinyLlama instead of Llama-2-7b:
```
LLM_MODEL=TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

**Slow inference**: Install PyTorch with CUDA support for GPU acceleration.

**Llama-2 access denied**: Make sure you've accepted the license on HuggingFace.

## Frontend Connection

The React frontend at `http://localhost:5173` (or 3000) is configured to call this backend. CORS is enabled for local development.
