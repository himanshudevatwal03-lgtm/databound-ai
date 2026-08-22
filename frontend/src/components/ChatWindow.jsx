import { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage.jsx";
import LoadingSpinner from "./LoadingSpinner.jsx";

/**
 * ChatWindow
 *
 * The scrollable message list, auto-scrolling to the newest message as
 * the conversation grows (including while the answer is still loading,
 * so the "thinking" indicator stays in view).
 */
export default function ChatWindow({ messages, isAnswering }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isAnswering]);

  return (
    <div className="chat-window">
      {messages.length === 0 && !isAnswering && (
        <div className="chat-empty-state">
          <p>Ask a question about your uploaded documents.</p>
          <p className="chat-empty-hint">Answers are grounded only in what you've uploaded — nothing else.</p>
        </div>
      )}

      {messages.map((message, i) => (
        <ChatMessage key={i} message={message} />
      ))}

      {isAnswering && (
        <div className="chat-message chat-message-assistant">
          <div className="card answer-card">
            <LoadingSpinner label="Thinking..." />
          </div>
        </div>
      )}

      <div ref={endRef} />
    </div>
  );
}
