# AluuGPT | Enterprise AI & Animation Platform

AluuGPT is a high-performance, enterprise-grade AI platform built with FastAPI and designed for seamless integration with OpenAI-compatible LLM providers. It features a stunning, dynamic UI with support for advanced chat capabilities, automated animation generation, and easy deployment to Vercel.

![AluuGPT Preview](https://via.placeholder.com/1200x600?text=AluuGPT+Enterprise+Interface)

## 🚀 Key Features

- **Advanced Chat Interface**: A premium, responsive UI with dark/light mode and micro-animations.
- **Multi-Model Support**: Easily switch between different LLM providers (Groq, Together AI, OpenAI, etc.) via `.env` configuration.
- **AI Animation Engine**: Generate dynamic animations directly from your prompts using a specialized rendering pipeline (triggered with the `[animation]` token).
- **Persistent Memory**: SQLite-backed chat history to keep track of your sessions.
- **Mathematical Support**: Full LaTeX rendering for technical and scientific explanations via KaTeX.
- **Enterprise Ready**: Optimized for production with support for serverless deployment on Vercel.

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn
- **Frontend**: HTML5, Vanilla CSS, Javascript
- **AI Integration**: OpenAI SDK (compatible with any OpenAI-style API)
- **Animation**: Pygame (for rendering), FFmpeg (for video encoding)
- **Database**: SQLite (local or `/tmp` for serverless)

## 📦 Project Structure

```text
AluuGPT/
├── api/                # Vercel serverless entry point
├── data/               # Persistent database storage
├── static/             # Frontend assets (HTML, CSS, JS)
│   └── animations/     # Local storage for generated videos
├── utils/              # Backend logic (chat, animation, etc.)
├── main.py             # Main FastAPI application
├── animScript.py       # Core animation rendering script
├── vercel.json         # Vercel deployment configuration
└── .env.example        # Environment variable template
```

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Gunjan5308A/aluuGPT.git
cd aluuGPT
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```
Ensure `BASE_URLS` includes the `/v1` suffix for OpenAI-compatible providers.

### 5. Run Locally
```bash
./start.sh
```
The application will be available at `http://localhost:8000`.

## ☁️ Vercel Deployment

AluuGPT is pre-configured for Vercel. To deploy:

1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` from the project root.
3. Add your environment variables in the Vercel dashboard.
4. Ensure `VERCEL=1` is set in your environment variables.

> [!NOTE]
> For animation generation on Vercel, the platform uses the writable `/tmp` directory. Ensure your API keys and models are correctly configured in the dashboard.

## 🎨 UI Controls

- **Think Token**: Wraps thoughts in `<|think|>` tags for detailed reasoning.
- **Fast Token**: Triggers high-speed response modes.
- **Animation Token**: Requests the AI to generate a visual animation based on the prompt.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with ❤️ by the AluuGPT Team.
