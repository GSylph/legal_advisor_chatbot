import { useState, useEffect, useRef } from "react";
import ReasoningTrace from "./ReasoningTrace";
import MarkdownMessage from "./MarkdownMessage";

/* ─── Icon components ─────────────────────────────────────────────── */

function IconArrowUp() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="19" x2="12" y2="5" />
      <polyline points="5 12 12 5 19 12" />
    </svg>
  );
}

function IconStop() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
      <rect x="4" y="4" width="16" height="16" rx="2" />
    </svg>
  );
}

function IconPaperclip() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
    </svg>
  );
}

function IconScale() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3v18M3 9l9-6 9 6M3 15l9 6 9-6" />
    </svg>
  );
}

function IconBolt() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  );
}

function IconDots() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
      <circle cx="5"  cy="12" r="1.8" />
      <circle cx="12" cy="12" r="1.8" />
      <circle cx="19" cy="12" r="1.8" />
    </svg>
  );
}

function IconShield() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="white" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}

/* ─── Action pill ─────────────────────────────────────────────────── */
function ActionPill({ icon, label, title }) {
  return (
    <button
      type="button"
      title={title || label}
      aria-label={title || label}
      className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-zinc-100 hover:bg-zinc-200/80 text-zinc-500 hover:text-zinc-700 text-xs font-medium transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-300"
    >
      {icon}
      {label && <span>{label}</span>}
    </button>
  );
}

/* ─── Loading dots ────────────────────────────────────────────────── */
function LoadingDots() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3" aria-label="Thinking" role="status">
      <span className="w-2 h-2 rounded-full bg-zinc-300 animate-dot-bounce-1" />
      <span className="w-2 h-2 rounded-full bg-zinc-300 animate-dot-bounce-2" />
      <span className="w-2 h-2 rounded-full bg-zinc-300 animate-dot-bounce-3" />
    </div>
  );
}

/* ─── User bubble ─────────────────────────────────────────────────── */
function UserBubble({ text }) {
  return (
    <div className="flex justify-end animate-msg-in">
      <div className="max-w-[72%] px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm leading-relaxed bg-zinc-200/95 text-zinc-900">
        {text}
      </div>
    </div>
  );
}

/* ─── Bot card ────────────────────────────────────────────────────── */
function BotCard({ text, ealai, streaming = false }) {
  return (
    <div className="flex justify-start items-start animate-msg-in">
      <div className="flex-shrink-0 mr-3 mt-0.5">
        <div className="w-7 h-7 rounded-full bg-zinc-800 flex items-center justify-center" aria-hidden="true">
          <IconShield />
        </div>
      </div>

      <div className="flex-1 min-w-0 max-w-[88%] rounded-2xl rounded-tl-sm border border-zinc-200/80 px-4 py-3 text-sm bg-white/95 shadow-card">
        {ealai?.warning && (
          <div className="mb-3 flex items-start gap-2 text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-xs font-medium">
            <svg className="flex-shrink-0 mt-0.5" width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L1 21h22L12 2zm0 3.5L20.5 19h-17L12 5.5zM11 10v4h2v-4h-2zm0 6v2h2v-2h-2z" />
            </svg>
            <span>{ealai.warning}</span>
          </div>
        )}

        <div className="bot-prose">
          <MarkdownMessage text={text} streaming={streaming} />
          {streaming && (
            <span
              aria-hidden="true"
              className="inline-block w-[2px] h-[1em] ml-0.5 bg-zinc-500 animate-blink align-text-bottom"
            />
          )}
        </div>

        {ealai && (
          <ReasoningTrace
            applicableLaw={ealai.applicableLaw}
            ruleMatched={ealai.ruleMatched}
            ruleStatute={ealai.ruleStatute}
            ruleSection={ealai.ruleSection}
            sources={ealai.sources}
            reasoning={ealai.reasoning}
            consistencyFlag={ealai.consistencyFlag}
            auditHash={ealai.auditHash}
            warning={ealai.warning}
          />
        )}
      </div>
    </div>
  );
}

/* ─── Input card ──────────────────────────────────────────────────── */
function InputCard({ value, onChange, onSubmit, onStop, disabled, streamState }) {
  const textareaRef = useRef(null);
  const isStreaming = streamState === "streaming" || streamState === "thinking";

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 180) + "px";
  }, [value]);

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (isStreaming) onStop();
      else onSubmit(e);
    }
  }

  return (
    <form onSubmit={onSubmit} className="w-full">
      <div className="bg-white rounded-card shadow-card focus-within:shadow-card-focus transition-shadow duration-[280ms] px-4 pt-3.5 pb-3">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything…"
          disabled={disabled && !isStreaming}
          rows={1}
          aria-label="Your legal question"
          className="w-full resize-none bg-transparent border-none outline-none text-sm text-zinc-800 placeholder-zinc-400 leading-relaxed overflow-hidden font-ui disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ maxHeight: "180px" }}
        />

        <div className="flex items-center justify-between mt-2.5 pt-2.5 border-t border-zinc-100 gap-2">
          <div className="flex items-center gap-1.5 flex-wrap">
            <ActionPill icon={<IconPaperclip />} label=""              title="Attach document" />
            <ActionPill icon={<IconScale />}     label="Legal Analysis" />
            <ActionPill icon={<IconBolt />}      label="Case Law"       />
            <ActionPill icon={<IconDots />}      label=""              title="More options"    />
          </div>

          {isStreaming ? (
            <button
              type="button"
              onClick={onStop}
              aria-label="Stop generating"
              className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full bg-zinc-700 text-white hover:bg-zinc-900 hover:scale-105 transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-zinc-600"
            >
              <IconStop />
            </button>
          ) : (
            <button
              type="submit"
              disabled={!value.trim() || disabled}
              aria-label="Send message"
              className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full bg-zinc-900 text-white hover:bg-zinc-700 hover:scale-105 hover:animate-send-pulse disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:bg-zinc-900 transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-zinc-600"
            >
              <IconArrowUp />
            </button>
          )}
        </div>
      </div>
    </form>
  );
}

/* ─── Welcome screen ──────────────────────────────────────────────── */
function WelcomeScreen({ input, onChange, onSubmit, onStop, disabled, streamState }) {
  const suggestions = [
    "What are my rights under Singapore's PDPA?",
    "Can my employer terminate me without notice?",
    "Is my rental contract legally enforceable?",
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full px-4 pb-10 pt-4">
      <h2 className="font-display animate-welcome-float text-[2.2rem] sm:text-[2.8rem] font-bold text-zinc-800 text-center mb-8 leading-tight">
        What can I help with?
      </h2>

      <div className="w-full max-w-2xl">
        <InputCard
          value={input}
          onChange={onChange}
          onSubmit={onSubmit}
          onStop={onStop}
          disabled={disabled}
          streamState={streamState}
        />
      </div>

      <div className="mt-5 flex flex-wrap gap-2 justify-center max-w-xl">
        {suggestions.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => onChange(s)}
            className="text-xs text-zinc-500 border border-zinc-300/80 rounded-full px-3 py-1.5 bg-white/60 hover:bg-white hover:border-zinc-400 hover:text-zinc-700 transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-300"
          >
            {s}
          </button>
        ))}
      </div>

      <p className="mt-8 text-[11px] text-zinc-400 text-center max-w-sm leading-relaxed">
        AI can make mistakes. Please double-check responses.
        <br />Not a substitute for qualified legal advice.
      </p>
    </div>
  );
}

/* ─── Main Chat component ─────────────────────────────────────────── */
export default function Chat() {
  const [messages,      setMessages]      = useState([]);
  const [input,         setInput]         = useState("");
  // "idle" | "thinking" | "streaming" | "complete" | "error"
  const [streamState,   setStreamState]   = useState("idle");
  const [error,         setError]         = useState(null);
  const [sessionId,     setSessionId]     = useState(null);
  const [backendStatus, setBackendStatus] = useState("checking");

  const pollRef          = useRef(null);
  const bottomRef        = useRef(null);
  const abortControllerRef = useRef(null);

  /* ── Backend health polling ──────────────────────────────────── */
  useEffect(() => {
    let cancelled = false;
    async function checkHealth() {
      try {
        const res = await fetch("/api/health", { signal: AbortSignal.timeout(3000) });
        if (!cancelled && res.ok) {
          setBackendStatus("ready");
          clearInterval(pollRef.current);
        }
      } catch {
        if (!cancelled) setBackendStatus("offline");
      }
    }
    checkHealth();
    pollRef.current = setInterval(checkHealth, 4000);
    return () => { cancelled = true; clearInterval(pollRef.current); };
  }, []);

  /* ── Scroll to bottom on new content ────────────────────────── */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamState]);

  /* ── Stop streaming ──────────────────────────────────────────── */
  function stopStreaming() {
    abortControllerRef.current?.abort();
    // Mark any still-streaming message as complete
    setMessages(prev => prev.map(m => m.streaming ? { ...m, streaming: false } : m));
    setStreamState("idle");
  }

  /* ── Send message (streaming) ────────────────────────────────── */
  async function sendMessage(e) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || streamState !== "idle") return;

    abortControllerRef.current?.abort();
    const controller = new AbortController();
    abortControllerRef.current = controller;

    const userMsg = { id: crypto.randomUUID(), sender: "user", text: trimmed };
    const botMsgId = crypto.randomUUID();
    const placeholder = { id: botMsgId, sender: "bot", text: "", streaming: true, ealai: null };

    setMessages(prev => [...prev, userMsg, placeholder]);
    setInput("");
    setError(null);
    setStreamState("thinking");

    try {
      const res = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, session_id: sessionId }),
        signal: controller.signal,
      });

      if (!res.ok) throw new Error(`API error: ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop(); // last chunk may be incomplete

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = JSON.parse(line.slice(6));

          if (payload.type === "token") {
            setStreamState(prev => prev === "thinking" ? "streaming" : prev);
            setMessages(prev => prev.map(m =>
              m.id === botMsgId ? { ...m, text: m.text + payload.text } : m
            ));
          }

          if (payload.type === "done" || payload.type === "refused") {
            const meta = payload.metadata;
            if (meta.session_id) {
            setSessionId(meta.session_id);
            localStorage.setItem("ealai_session_id", meta.session_id);
          }
            setMessages(prev => prev.map(m =>
              m.id === botMsgId ? {
                ...m,
                text: payload.type === "refused" ? (meta.answer || m.text) : m.text,
                streaming: false,
                ealai: {
                  applicableLaw:   meta.structured?.applicable_law,
                  ruleMatched:     meta.structured?.rule_result?.rule_matched,
                  ruleStatute:     meta.structured?.rule_result?.statute,
                  ruleSection:     meta.structured?.rule_result?.section,
                  sources:         meta.structured?.context_sources || [],
                  reasoning:       meta.structured?.reasoning,
                  consistencyFlag: meta.consistency_flag,
                  auditHash:       meta.audit_hash,
                  warning:         meta.warning,
                },
              } : m
            ));
            setStreamState("idle");
          }

          if (payload.type === "error") {
            throw new Error(payload.message);
          }
        }
      }
    } catch (err) {
      if (err.name === "AbortError") {
        // User cancelled — keep partial text, just stop streaming
        setMessages(prev => prev.map(m => m.streaming ? { ...m, streaming: false } : m));
        setStreamState("idle");
        return;
      }
      setError(err.message || "Failed to contact chatbot API");
      setMessages(prev => prev.filter(m => m.id !== botMsgId));
      setStreamState("error");
    } finally {
      setStreamState(prev =>
        prev === "thinking" || prev === "streaming" ? "idle" : prev
      );
    }
  }

  const backendReady  = backendStatus === "ready";
  const hasMessages   = messages.length > 0;
  const inputDisabled = !backendReady;

  return (
    <div className="relative flex flex-col h-full overflow-hidden">

      {!hasMessages && (
        <WelcomeScreen
          input={input}
          onChange={setInput}
          onSubmit={sendMessage}
          onStop={stopStreaming}
          disabled={inputDisabled}
          streamState={streamState}
        />
      )}

      {hasMessages && (
        <>
          <div className="flex-1 overflow-y-auto px-4 py-6">
            <div className="max-w-2xl mx-auto space-y-5">
              {messages.map((msg) =>
                msg.sender === "user"
                  ? <UserBubble key={msg.id} text={msg.text} />
                  : <BotCard   key={msg.id} text={msg.text} ealai={msg.ealai} streaming={msg.streaming} />
              )}

              {/* "Thinking" spinner — shown before first token arrives */}
              {streamState === "thinking" && messages[messages.length - 1]?.text === "" && (
                <div className="flex justify-start items-start animate-msg-in">
                  <div className="flex-shrink-0 mr-3 mt-0.5">
                    <div className="w-7 h-7 rounded-full bg-zinc-800 flex items-center justify-center" aria-hidden="true">
                      <IconShield />
                    </div>
                  </div>
                  <div className="rounded-2xl rounded-tl-sm border border-zinc-200/80 bg-white/95 shadow-card">
                    <LoadingDots />
                  </div>
                </div>
              )}

              {error && (
                <div className="flex justify-center animate-msg-in" role="alert">
                  <div className="bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl px-4 py-2.5 max-w-sm text-center">
                    {error}
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>
          </div>

          <div className="flex-shrink-0 px-4 pb-4 pt-2 border-t border-zinc-200/60">
            <div className="max-w-2xl mx-auto">
              <InputCard
                value={input}
                onChange={setInput}
                onSubmit={sendMessage}
                onStop={stopStreaming}
                disabled={inputDisabled}
                streamState={streamState}
              />
              <p className="mt-2 text-center text-[11px] text-zinc-400 select-none">
                AI can make mistakes. Please double-check responses.
              </p>
            </div>
          </div>
        </>
      )}

      {backendStatus !== "ready" && (
        <div
          role="status"
          aria-live="polite"
          className="animate-status-up absolute bottom-24 left-1/2 -translate-x-1/2 z-20 pointer-events-none"
        >
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium shadow-lg whitespace-nowrap ${backendStatus === "checking" ? "bg-zinc-800 text-zinc-200" : "bg-red-600 text-white"}`}>
            <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${backendStatus === "checking" ? "bg-amber-400 animate-pulse" : "bg-red-300"}`} />
            {backendStatus === "checking" ? "Connecting to backend…" : "Backend offline — retrying"}
          </div>
        </div>
      )}
    </div>
  );
}
