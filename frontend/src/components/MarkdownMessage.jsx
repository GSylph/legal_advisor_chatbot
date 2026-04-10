import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/* ─── Legal section config ────────────────────────────────────────── */
const LEGAL_SECTIONS = {
  "APPLICABLE LAW":  { border: "border-blue-400",   bg: "bg-blue-50",   label: "text-blue-700"   },
  "REASONING":       { border: "border-violet-400",  bg: "bg-violet-50", label: "text-violet-700" },
  "ANSWER":          { border: "border-emerald-400", bg: "bg-emerald-50",label: "text-emerald-700"},
  "LIMITATIONS":     { border: "border-amber-400",   bg: "bg-amber-50",  label: "text-amber-700"  },
  "IMPORTANT NOTE":  { border: "border-amber-400",   bg: "bg-amber-50",  label: "text-amber-700"  },
  "DISCLAIMER":      { border: "border-zinc-300",    bg: "bg-zinc-50",   label: "text-zinc-500"   },
};

/* ─── Parse raw LLM text into named sections ──────────────────────── */
// Matches: "1. APPLICABLE LAW", "APPLICABLE LAW", "**APPLICABLE LAW**"
const HEADER_RE = /^(?:\d+\.\s+)?(?:\*\*)?([A-Z][A-Z /]+[A-Z])(?:\*\*)?\s*$/m;

function parseSections(text) {
  const lines = text.split("\n");
  const sections = [];
  let current = { heading: null, lines: [] };

  for (const line of lines) {
    const match = line.match(/^(?:\d+\.\s+)?(?:\*\*)?([A-Z][A-Z /]+[A-Z])(?:\*\*)?\s*$/);
    const knownHeading = match && LEGAL_SECTIONS[match[1].trim()];
    if (knownHeading) {
      if (current.lines.length > 0 || current.heading) {
        sections.push({ heading: current.heading, body: current.lines.join("\n").trim() });
      }
      current = { heading: match[1].trim(), lines: [] };
    } else {
      current.lines.push(line);
    }
  }
  if (current.lines.length > 0 || current.heading) {
    sections.push({ heading: current.heading, body: current.lines.join("\n").trim() });
  }
  return sections;
}

/* ─── Custom react-markdown renderers ────────────────────────────── */
const mdComponents = {
  p:          ({ children }) => <p className="text-[13.5px] leading-relaxed text-zinc-700 mb-2 last:mb-0">{children}</p>,
  ul:         ({ children }) => <ul className="list-disc list-inside space-y-0.5 mb-2 pl-1 text-zinc-700">{children}</ul>,
  ol:         ({ children }) => <ol className="list-decimal list-inside space-y-0.5 mb-2 pl-1 text-zinc-700">{children}</ol>,
  li:         ({ children }) => <li className="text-[13.5px] leading-relaxed">{children}</li>,
  strong:     ({ children }) => <strong className="font-semibold text-zinc-800">{children}</strong>,
  em:         ({ children }) => <em className="italic text-zinc-600">{children}</em>,
  blockquote: ({ children }) => <blockquote className="border-l-2 border-zinc-300 pl-3 text-zinc-500 italic my-2">{children}</blockquote>,
  // Headings inside sections — de-emphasise since section titles are already styled
  h1: ({ children }) => <p className="font-semibold text-zinc-800 text-sm mb-1">{children}</p>,
  h2: ({ children }) => <p className="font-semibold text-zinc-800 text-sm mb-1">{children}</p>,
  h3: ({ children }) => <p className="font-semibold text-zinc-700 text-[13px] mb-1">{children}</p>,
  h4: ({ children }) => <p className="font-medium text-zinc-600 text-[13px] mb-1">{children}</p>,
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noopener noreferrer"
      className="text-blue-600 underline hover:text-blue-800 transition-colors">
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="overflow-x-auto my-2">
      <table className="w-full border-collapse text-xs">{children}</table>
    </div>
  ),
  th: ({ children }) => <th className="border border-zinc-200 bg-zinc-50 px-2 py-1 text-left font-semibold text-zinc-700">{children}</th>,
  td: ({ children }) => <td className="border border-zinc-200 px-2 py-1 text-zinc-600">{children}</td>,
  code: ({ inline, className, children }) => {
    if (inline) {
      return <code className="font-mono text-[12px] bg-zinc-100 text-zinc-700 px-1.5 py-0.5 rounded">{children}</code>;
    }
    return (
      <pre className="overflow-x-auto bg-zinc-900 rounded-xl p-3 my-2">
        <code className="text-zinc-100 text-[12px] font-mono whitespace-pre">{children}</code>
      </pre>
    );
  },
};

/* ─── Rendered body of one section ───────────────────────────────── */
function SectionBody({ body }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
      {body}
    </ReactMarkdown>
  );
}

/* ─── Full markdown message ───────────────────────────────────────── */
export default function MarkdownMessage({ text, streaming = false }) {
  if (!text) return null;

  if (streaming) {
    // Split at last double-newline: stable prefix → full markdown,
    // active suffix → plain text (avoids flicker from incomplete tokens)
    const boundary = text.lastIndexOf("\n\n");
    const stable = boundary > 0 ? text.slice(0, boundary) : "";
    const active  = boundary > 0 ? text.slice(boundary)   : text;
    return (
      <>
        {stable && <MarkdownBody text={stable} />}
        <span className="whitespace-pre-wrap text-[13.5px] leading-relaxed text-zinc-700">
          {active}
        </span>
      </>
    );
  }

  return <MarkdownBody text={text} />;
}

function MarkdownBody({ text }) {
  const sections = parseSections(text);

  // If no named sections found, render as plain markdown
  if (sections.length === 1 && !sections[0].heading) {
    return <SectionBody body={sections[0].body} />;
  }

  return (
    <div className="space-y-3">
      {sections.map((sec, i) => {
        const style = sec.heading ? LEGAL_SECTIONS[sec.heading] : null;
        if (!style) {
          // Pre-section preamble (no heading)
          return sec.body ? <SectionBody key={i} body={sec.body} /> : null;
        }
        return (
          <div key={i} className={`rounded-lg border-l-[3px] ${style.border} ${style.bg} px-3 pt-2 pb-2`}>
            <p className={`text-[10px] uppercase tracking-widest font-semibold mb-1.5 ${style.label}`}>
              {sec.heading}
            </p>
            <SectionBody body={sec.body} />
          </div>
        );
      })}
    </div>
  );
}
