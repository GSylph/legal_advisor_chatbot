import { useNavigate } from "react-router-dom";
import ProfileHeader      from "../components/profile/ProfileHeader.jsx";
import AccountSettingsForm from "../components/profile/AccountSettingsForm.jsx";
import UsageStatsCards    from "../components/profile/UsageStatsCards.jsx";
import ApiKeyManager      from "../components/profile/ApiKeyManager.jsx";
import AuditLogDownload   from "../components/profile/AuditLogDownload.jsx";

export default function ProfilePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#EBEBEB] font-ui">
      {/* Minimal top bar */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-zinc-200/80 bg-[#EBEBEB]">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-900 transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 rounded-lg px-1"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6" />
          </svg>
          Back
        </button>

        <span className="font-display text-sm font-semibold text-zinc-700">Profile</span>

        <button
          onClick={() => navigate("/app")}
          className="text-sm text-zinc-500 hover:text-zinc-900 transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 rounded-lg px-1"
        >
          Open App →
        </button>
      </header>

      {/* Content */}
      <main className="max-w-2xl mx-auto px-5 py-10 space-y-5">
        <ProfileHeader />
        <AccountSettingsForm />
        <UsageStatsCards />
        <ApiKeyManager />
        <AuditLogDownload />

        <p className="text-center text-[11px] text-zinc-400 pb-6">
          EALAI Research Build · Singapore Law · JURIX 2025
        </p>
      </main>
    </div>
  );
}
