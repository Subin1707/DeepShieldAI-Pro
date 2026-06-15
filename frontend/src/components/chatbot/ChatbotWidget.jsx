import { MessageCircle, Send, X } from "lucide-react";
import { useState } from "react";

import useChatbot from "../../hooks/useChatbot";
import ChatMessage from "./ChatMessage.jsx";
import SuggestedQuestions from "./SuggestedQuestions.jsx";

function ChatbotWidget() {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const { messages, suggestions, loading, sendMessage } = useChatbot();

  const submit = async (event) => {
    event?.preventDefault();
    const text = draft;
    setDraft("");
    await sendMessage(text);
  };

  return (
    <div className="fixed bottom-5 right-5 z-50">
      {open && (
        <section className="mb-3 flex h-[32rem] w-[min(calc(100vw-2.5rem),24rem)] flex-col overflow-hidden rounded-lg border border-shield-line bg-shield-panel shadow-glow">
          <header className="flex items-center justify-between border-b border-shield-line px-4 py-3">
            <div>
              <h3 className="font-semibold text-white">DeepShield Assistant</h3>
              <p className="text-xs text-slate-500">Ask about verdict, confidence and risk signals</p>
            </div>
            <button type="button" onClick={() => setOpen(false)} className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white">
              <X size={18} />
            </button>
          </header>

          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {messages.map((message, index) => (
              <ChatMessage key={`${message.role}-${index}`} role={message.role} content={message.content} />
            ))}
            {loading && <ChatMessage role="assistant" content="Thinking through the analysis..." />}
          </div>

          <SuggestedQuestions
            questions={suggestions}
            onSelect={(question) => {
              setDraft("");
              sendMessage(question);
            }}
          />

          <form onSubmit={submit} className="flex gap-2 border-t border-shield-line p-3">
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask a question..."
              className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-cyan-400"
            />
            <button
              type="submit"
              disabled={loading || !draft.trim()}
              className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-400 text-slate-950 disabled:opacity-50"
            >
              <Send size={18} />
            </button>
          </form>
        </section>
      )}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-cyan-400 text-slate-950 shadow-glow hover:bg-cyan-300"
        aria-label="Open chatbot"
      >
        <MessageCircle size={24} />
      </button>
    </div>
  );
}

export default ChatbotWidget;
