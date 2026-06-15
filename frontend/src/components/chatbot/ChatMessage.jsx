import { Bot, User } from "lucide-react";

function ChatMessage({ role, content }) {
  const isUser = role === "user";
  const Icon = isUser ? User : Bot;

  return (
    <div className={`flex gap-2 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-cyan-400/10 text-cyan-200">
          <Icon size={15} />
        </div>
      )}
      <div
        className={`max-w-[85%] rounded-lg px-3 py-2 text-sm leading-6 ${
          isUser ? "bg-cyan-400 text-slate-950" : "bg-slate-900 text-slate-200"
        }`}
      >
        {content}
      </div>
    </div>
  );
}

export default ChatMessage;
