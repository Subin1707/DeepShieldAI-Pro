function SuggestedQuestions({ questions = [], onSelect }) {
  if (!questions.length) return null;

  return (
    <div className="flex flex-wrap gap-2 border-t border-shield-line p-3">
      {questions.slice(0, 3).map((question) => (
        <button
          key={question}
          type="button"
          onClick={() => onSelect(question)}
          className="rounded-full border border-cyan-400/20 px-3 py-1 text-left text-xs text-cyan-100 hover:bg-cyan-400/10"
        >
          {question}
        </button>
      ))}
    </div>
  );
}

export default SuggestedQuestions;
