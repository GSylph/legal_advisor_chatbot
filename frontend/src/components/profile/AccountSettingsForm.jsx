import { useState } from "react";

export default function AccountSettingsForm() {
  const [displayName,   setDisplayName]   = useState(() => localStorage.getItem("ealai_display_name")   ?? "Legal Advisor");
  const [jurisdiction,  setJurisdiction]  = useState(() => localStorage.getItem("ealai_jurisdiction")   ?? "singapore");
  const [saved, setSaved] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    localStorage.setItem("ealai_display_name", displayName);
    localStorage.setItem("ealai_jurisdiction", jurisdiction);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  const inputClass = "w-full bg-white border border-zinc-200 rounded-xl px-4 py-2.5 text-sm text-zinc-800 focus:outline-none focus:border-zinc-400 focus:ring-2 focus:ring-zinc-100 transition-all duration-150";
  const labelClass = "block text-[11px] font-semibold uppercase tracking-wider text-zinc-400 mb-1.5";

  return (
    <div className="bg-white rounded-2xl shadow-card border border-zinc-100 p-7">
      <h2 className="font-semibold text-zinc-800 text-base mb-6">Account Settings</h2>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="display-name" className={labelClass}>Display Name</label>
          <input
            id="display-name"
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            className={inputClass}
          />
        </div>

        <div>
          <label htmlFor="email" className={labelClass}>Email</label>
          <input
            id="email"
            type="email"
            value="la@ealai.research"
            readOnly
            className={`${inputClass} opacity-50 cursor-not-allowed`}
          />
        </div>

        <div>
          <label htmlFor="jurisdiction" className={labelClass}>Jurisdiction</label>
          <select
            id="jurisdiction"
            value={jurisdiction}
            onChange={(e) => setJurisdiction(e.target.value)}
            className={inputClass}
          >
            <option value="singapore">Singapore</option>
            <option value="general" disabled>General (coming soon)</option>
          </select>
        </div>

        <div className="flex items-center gap-3 pt-1">
          <button
            type="submit"
            className="px-5 py-2.5 rounded-full bg-zinc-900 text-white text-sm font-semibold hover:bg-zinc-700 transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-700"
          >
            {saved ? "Saved ✓" : "Save Changes"}
          </button>
          {saved && <span className="text-sm text-emerald-600 font-medium animate-msg-in">Settings updated</span>}
        </div>
      </form>
    </div>
  );
}
