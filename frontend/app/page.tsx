"use client";

import { ChangeEvent, FormEvent, useState } from "react";

type Message = { role: "user" | "assistant"; content: string };
type View = "chat" | "summary";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [view, setView] = useState<View>("chat");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [summaryStatus, setSummaryStatus] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedMessage = message.trim();
    if (!trimmedMessage || isLoading) return;

    setMessages((current) => [...current, { role: "user", content: trimmedMessage }]);
    setMessage("");
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmedMessage }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok || !data?.response) {
        throw new Error(data?.detail ?? "StudyX AI could not answer right now.");
      }
      setMessages((current) => [...current, { role: "assistant", content: data.response }]);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to send your message.");
    } finally {
      setIsLoading(false);
    }
  }

  function choosePdf(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setError(null);
    setSummary(null);
    if (!file) return;
    if (file.type !== "application/pdf" || !file.name.toLowerCase().endsWith(".pdf")) {
      setSelectedFile(null);
      setError("Please select a PDF file.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setSelectedFile(null);
      setError("PDF files must be 10 MB or smaller.");
      return;
    }
    setSelectedFile(file);
  }

  async function generateSummary(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile || isLoading) return;

    setError(null);
    setSummary(null);
    setIsLoading(true);
    setUploadProgress(0);
    setSummaryStatus("Uploading your PDF…");

    try {
      const result = await new Promise<{ summary: string }>((resolve, reject) => {
        const request = new XMLHttpRequest();
        const data = new FormData();
        data.append("file", selectedFile);
        request.open("POST", `${API_BASE_URL}/api/summaries/pdf`);
        request.responseType = "json";
        request.upload.onprogress = (progressEvent) => {
          if (progressEvent.lengthComputable) {
            setUploadProgress(Math.round((progressEvent.loaded / progressEvent.total) * 70));
          }
        };
        request.upload.onload = () => {
          setUploadProgress(80);
          setSummaryStatus("Extracting text and generating your study summary…");
        };
        request.onload = () => {
          const data = request.response;
          if (request.status < 200 || request.status >= 300 || !data?.summary) {
            reject(new Error(data?.detail ?? "StudyX AI could not summarize this PDF."));
            return;
          }
          setUploadProgress(100);
          resolve(data);
        };
        request.onerror = () => reject(new Error("Unable to reach the StudyX AI backend."));
        request.send(data);
      });
      setSummary(result.summary);
      setSummaryStatus(null);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to upload the PDF.");
      setSummaryStatus(null);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="shell">
      <section className="chat-card" aria-label="StudyX AI chat">
        <header className="header">
          <div className="brand-mark" aria-hidden="true">S</div>
          <div>
            <p className="eyebrow">STUDYX AI</p>
            <h1>Your study companion</h1>
          </div>
          <nav className="nav-tabs" aria-label="StudyX AI features">
            <button className={view === "chat" ? "active" : ""} onClick={() => { setView("chat"); setError(null); }}>Chat</button>
            <button className={view === "summary" ? "active" : ""} onClick={() => { setView("summary"); setError(null); }}>PDF Summary</button>
          </nav>
        </header>

        {view === "chat" ? <>
        <div className="conversation" aria-live="polite">
          {messages.length === 0 ? (
            <div className="empty-state">
              <p className="spark">✦</p>
              <h2>What are you learning today?</h2>
              <p>Ask in English, Hindi, or Hinglish. I’ll explain it clearly.</p>
              <button type="button" onClick={() => setMessage("Explain Machine Learning in simple Hindi.")}>Try a Hindi question</button>
            </div>
          ) : (
            messages.map((item, index) => (
              <article className={`message ${item.role}`} key={`${item.role}-${index}`}>
                <span>{item.role === "assistant" ? "SX" : "You"}</span>
                <p>{item.content}</p>
              </article>
            ))
          )}
          {isLoading && <div className="thinking"><span /> StudyX AI is thinking…</div>}
        </div>

        <form className="composer" onSubmit={sendMessage}>
          <label className="sr-only" htmlFor="message">Your question</label>
          <textarea
            id="message"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Ask anything about your studies…"
            rows={1}
            maxLength={4000}
            disabled={isLoading}
          />
          <button type="submit" disabled={!message.trim() || isLoading}>
            {isLoading ? "Sending" : "Send"}
          </button>
        </form>
        </> : <section className="summary-view" aria-live="polite">
          <div className="summary-intro">
            <p className="spark">✦</p>
            <h2>Turn a PDF into revision notes</h2>
            <p>Upload text-based study notes and get a clear AI summary. PDFs up to 10 MB are supported.</p>
          </div>
          <form className="upload-form" onSubmit={generateSummary}>
            <label className="file-picker" htmlFor="pdf-file">
              <input id="pdf-file" type="file" accept="application/pdf,.pdf" onChange={choosePdf} disabled={isLoading} />
              <strong>{selectedFile ? selectedFile.name : "Choose a PDF"}</strong>
              <span>{selectedFile ? `${Math.ceil(selectedFile.size / 1024)} KB selected` : "PDF only · 10 MB maximum"}</span>
            </label>
            <button className="summary-button" type="submit" disabled={!selectedFile || isLoading}>
              {isLoading ? "Creating summary…" : "Generate summary"}
            </button>
          </form>
          {isLoading && <div className="upload-status"><div><span style={{ width: `${uploadProgress}%` }} /></div><p>{summaryStatus}</p></div>}
          {summary && <article className="summary-result"><p className="eyebrow">STUDY SUMMARY</p><div>{summary}</div></article>}
        </section>}
        {error && <p className="error" role="alert">{error}</p>}
        <p className="note">StudyX AI can make mistakes. Double-check important information.</p>
      </section>
    </main>
  );
}
