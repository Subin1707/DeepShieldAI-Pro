import { useEffect, useMemo, useState } from "react";

import { explainAnalysis, getSuggestedQuestions } from "../services/chatbotService";

const fallbackSuggestions = [
  "Vì sao hệ thống đưa ra kết luận này?",
  "Vùng nào đáng nghi nhất?",
  "Mình nên kiểm tra thủ công thế nào?",
  "Chatbot đang dùng AI thật hay fallback?",
];

function getLatestAnalysis() {
  try {
    const raw = localStorage.getItem("latestAnalysisResult");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function useChatbot() {
  const analysis = useMemo(() => getLatestAnalysis(), []);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Mình có thể trả lời câu hỏi tự do nếu backend đã cấu hình API AI thật. Nếu chưa có API key, mình sẽ nói rõ đang ở chế độ fallback.",
    },
  ]);
  const [suggestions, setSuggestions] = useState(fallbackSuggestions);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getSuggestedQuestions()
      .then((data) => {
        if (Array.isArray(data) && data.length) setSuggestions(data);
      })
      .catch(() => setSuggestions(fallbackSuggestions));
  }, []);

  const sendMessage = async (content) => {
    const text = content.trim();
    if (!text || loading) return;

    setMessages((items) => [...items, { role: "user", content: text }]);
    setLoading(true);

    try {
      const response = await explainAnalysis({ question: text, analysis });
      const answer = response?.answer || response?.report || response?.message || response?.explanation || "Mình chưa tạo được câu trả lời cho câu hỏi này.";
      setMessages((items) => [...items, { role: "assistant", content: answer }]);
    } catch {
      setMessages((items) => [
        ...items,
        {
          role: "assistant",
          content: "Chatbot API đang lỗi hoặc backend chưa chạy. Bạn kiểm tra backend ở cổng 8000 và cấu hình GROQ_API_KEY hoặc GEMINI_API_KEY nếu muốn trả lời tự do bằng AI thật.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return { messages, suggestions, loading, sendMessage };
}

export default useChatbot;
