import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "./pages/LandingPage.jsx";
import AppShell    from "./AppShell.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"        element={<LandingPage />} />
        <Route path="/app"     element={<AppShell />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="*"        element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
