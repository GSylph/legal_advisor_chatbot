export default function ProfileHeader() {
  const name        = localStorage.getItem("ealai_display_name") ?? "Legal Advisor";
  const joinedDate  = "April 2026";

  return (
    <div className="bg-white rounded-2xl shadow-card border border-zinc-100 p-7 flex items-center gap-6">
      {/* Avatar */}
      <div className="w-20 h-20 rounded-full bg-zinc-900 text-white flex items-center justify-center font-display text-2xl font-black flex-shrink-0 select-none">
        LA
      </div>

      {/* Info */}
      <div>
        <h1 className="font-display text-2xl font-black text-zinc-900 mb-1">{name}</h1>
        <div className="flex items-center gap-2 flex-wrap">
          <span className="inline-flex items-center gap-1.5 bg-zinc-900 text-white text-[11px] font-semibold px-3 py-1 rounded-full">
            <svg width="9" height="9" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
            </svg>
            Research User
          </span>
          <span className="text-xs text-zinc-400">Member since {joinedDate}</span>
        </div>
        <p className="text-sm text-zinc-400 mt-1.5">la@ealai.research</p>
      </div>
    </div>
  );
}
