import { useState } from "react";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  async function sendMessage(e) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const userMessage = {
      id: crypto.randomUUID(),
      sender: "user",
      text: trimmed
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setError(null);
    setIsLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: trimmed })
      });

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }

      const data = await res.json();

      const botMessage = {
        id: crypto.randomUUID(),
        sender: "bot",
        text: data.formatted_text || data.raw_text
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "Failed to contact chatbot API";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="bg-gradient-to-b from-zinc-900 to-neutral-950 border border-zinc-800 rounded-2xl shadow-2xl flex flex-col h-[75vh] p-4">
      <div className="flex-1 overflow-y-auto space-y-2 mb-3 pr-1">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[75%] rounded-xl px-3 py-2 text-sm ${m.sender === "user"
                  ? "bg-zinc-700 text-zinc-50"
                  : "bg-zinc-800 text-zinc-100"
                }`}
            >
              <div className="text-[0.7rem] font-semibold text-zinc-300 mb-1">
                {m.sender === "user" ? "You" : "Legal Advisor"}
              </div>
              <div className="whitespace-pre-wrap">{m.text}</div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[75%] rounded-xl px-3 py-2 text-sm bg-zinc-800 text-zinc-100">
              <div className="text-[0.7rem] font-semibold text-zinc-300 mb-1">
                Legal Advisor
              </div>
              <div>Thinking...</div>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mb-2 text-xs rounded-md bg-red-900 text-red-100 px-3 py-2">
          Error: {error}
        </div>
      )}

      <form
        className="flex gap-2 border-t border-zinc-700 pt-2"
        onSubmit={sendMessage}
      >
        <input
          type="text"
          placeholder="Describe your legal situation..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
          className="flex-1 rounded-full border border-zinc-600 bg-zinc-950 text-zinc-100 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-500"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="rounded-full bg-zinc-300 text-zinc-950 font-semibold px-4 py-2 text-sm hover:bg-zinc-200 disabled:opacity-60"
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
}

