import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

ROOT = Path(__file__).resolve().parent
INDEX_FILE = ROOT / "index.html"

load_dotenv(dotenv_path=ROOT.parent / ".env")

CONTEXT = """
500 Days of Summer is a 2009 romantic comedy-drama film directed by Marc Webb.
The story follows Tom Hansen, a greeting card writer, and Summer Finn, the new assistant at the office where he works.
The film is known for its nonlinear storytelling and its focus on the relationship between Tom and Summer.
The movie explores themes of love, heartbreak, and expectations.
The main character is Tom Hansen, played by Joseph Gordon-Levitt.
Summer Finn is played by Zooey Deschanel.
The movie was written by Scott Neustadter and Michael H. Weber.
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            content = INDEX_FILE.read_text(encoding="utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/api/ask":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        data = json.loads(raw or "{}")
        query = data.get("query", "")

        answer = self.get_answer(query)
        payload = json.dumps({"answer": answer}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def get_answer(self, query):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "No GROQ API key found. Please set GROQ_API_KEY in the environment."

        client = Groq(api_key=api_key)
        prompt = f"""
You are a helpful assistant.
Answer ONLY using the context below.
If the answer is not present, say: "No information available in the provided context."

Context:
{CONTEXT}

Question:
{query}

Answer:
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            return f"Error calling Groq: {exc}"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving at http://localhost:{port}")
    server.serve_forever()
