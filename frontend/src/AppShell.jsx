import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Chat from "./components/Chat.jsx";

function IconMenu() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <line x1="3"  y1="6"  x2="21" y2="6"  />
      <line x1="3"  y1="12" x2="21" y2="12" />
      <line x1="3"  y1="18" x2="21" y2="18" />
    </svg>
  );
}

function IconPlus() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5"  y1="12" x2="19" y2="12" />
    </svg>
  );
}

function IconSearch() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="7" />
      <line x1="16.5" y1="16.5" x2="22" y2="22" />
    </svg>
  );
}

function IconBookmark() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z" />
    </svg>
  );
}

function IconHome() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H5a1 1 0 01-1-1V9.5z" />
      <path d="M9 21V12h6v9" />
    </svg>
  );
}

function IconStar() {
  return (
    <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
    </svg>
  );
}

function SidebarItem({ icon, label, onClick, highlight = false }) {
  return (
    <button
      onClick={onClick}
      title={label}
      aria-label={label}
      className={`
        flex items-center gap-3 w-full rounded-xl px-3 py-2.5
        transition-colors duration-200
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-zinc-400
        ${highlight
          ? "bg-zinc-900 text-white hover:bg-zinc-700"
          : "text-zinc-500 hover:bg-zinc-200/80 hover:text-zinc-800"}
      `}
    >
      <span className="flex-shrink-0 flex items-center justify-center w-5 h-5">{icon}</span>
      <span className="sidebar-label text-sm font-medium leading-none">{label}</span>
    </button>
  );
}

export default function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <div className="flex h-screen overflow-hidden font-ui">

      <aside
        className={`sidebar${sidebarOpen ? " open" : ""} flex flex-col py-4 px-2 gap-1 border-r border-zinc-200/80 bg-[#E0E0E0]`}
        aria-label="Sidebar navigation"
      >
        <button
          onClick={() => setSidebarOpen((v) => !v)}
          title={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          aria-expanded={sidebarOpen}
          className="flex items-center justify-center w-10 h-10 rounded-xl mb-1.5 self-center text-zinc-500 hover:bg-zinc-200/80 hover:text-zinc-800 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400"
        >
          <IconMenu />
        </button>

        <SidebarItem icon={<IconPlus />} label="New chat" highlight onClick={() => window.location.reload()} />

        <div className="my-2 h-px bg-zinc-300/70 mx-1" role="separator" />

        <SidebarItem icon={<IconSearch />}   label="Search"  />
        <SidebarItem icon={<IconBookmark />} label="Library" />
        <SidebarItem icon={<IconHome />}     label="Home"    onClick={() => navigate("/")} />
      </aside>

      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <header className="flex items-center justify-between px-5 py-3 border-b border-zinc-200/80 flex-shrink-0 bg-[#EBEBEB]">
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 rounded-lg px-1"
          >
            <span className="text-sm font-semibold tracking-tight font-display hover:text-zinc-600 transition-colors duration-150">EALAI</span>
            <span className="hidden sm:inline text-[11px] font-normal text-zinc-400 mt-0.5">
              Explainable Legal AI · Singapore
            </span>
          </button>

          <div className="flex items-center gap-2.5">
            <div className="hidden sm:flex items-center gap-1.5 bg-zinc-900 text-white text-[11px] font-semibold px-3 py-1.5 rounded-full select-none">
              <IconStar />
              Research Build
            </div>
            <button
              onClick={() => navigate("/profile")}
              className="w-8 h-8 rounded-full bg-zinc-800 text-white flex items-center justify-center text-[11px] font-bold select-none flex-shrink-0 hover:bg-zinc-700 transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400"
              aria-label="Go to profile"
            >
              LA
            </button>
          </div>
        </header>

        <main className="flex-1 min-h-0 overflow-hidden">
          <Chat />
        </main>
      </div>
    </div>
  );
}
