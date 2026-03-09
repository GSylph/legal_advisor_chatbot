import Chat from "./components/Chat.jsx";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col items-center bg-slate-900 text-slate-100 px-4 py-8">
      <header className="text-center mb-6">
        <h1 className="text-2xl font-semibold">Singapore Legal Advisor Chatbot</h1>
        <p className="mt-2 text-slate-400">
          Ask legal questions and get structured guidance.
        </p>
      </header>
      <main className="w-full max-w-3xl">
        <Chat />
      </main>
    </div>
  );
}

