import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as api from "../services/api.js";
import ChatWindow from "../components/ChatWindow.jsx";
import DocumentSelector from "../components/DocumentSelector.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";

const ANSWER_STYLES = [
  { value: "detailed", label: "Detailed" },
  { value: "short", label: "Short" },
  { value: "bullet_points", label: "Bullet points" },
  { value: "simple", label: "Simple" },
];

/**
 * Chat
 *
 * The question-answering interface (spec section 18). This phase's chat
 * is intentionally session-only — messages live in React state and
 * vanish on refresh. Persisted conversation history with real follow-up
 * context (spec section 18's "maintain conversation context") is Phase
 * 7's job; this page proves the underlying grounded-answer pipeline
 * (Phases 4-5) end to end first.
 */
export default function Chat() {
  const [documents, setDocuments] = useState([]);
  const [collections, setCollections] = useState([]);
  const [loadingContext, setLoadingContext] = useState(true);

  const [scope, setScope] = useState(null); // null | {type: "document"|"collection", id}
  const [answerStyle, setAnswerStyle] = useState("detailed");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isAnswering, setIsAnswering] = useState(false);

  useEffect(() => {
    Promise.all([api.listDocuments(), api.listCollections()])
      .then(([docs, cols]) => {
        setDocuments(docs.filter((d) => d.status === "ready"));
        setCollections(cols);
      })
      .finally(() => setLoadingContext(false));
  }, []);

  async function handleSend(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || isAnswering) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setIsAnswering(true);

    try {
      const result = await api.askQuestion({
        question,
        documentId: scope?.type === "document" ? scope.id : undefined,
        collectionId: scope?.type === "collection" ? scope.id : undefined,
        answerStyle,
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", answer: result.answer, supported: result.supported, sources: result.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "error", text: err.message }]);
    } finally {
      setIsAnswering(false);
    }
  }

  if (loadingContext) {
    return (
      <main>
        <div className="container chat-page">
          <LoadingSpinner label="Loading your documents..." />
        </div>
      </main>
    );
  }

  if (documents.length === 0) {
    return (
      <main>
        <div className="container chat-page">
          <h1>Chat</h1>
          <p className="empty-state">
            You don't have any processed documents yet. <Link to="/documents">Upload one first →</Link>
          </p>
        </div>
      </main>
    );
  }

  return (
    <main>
      <div className="container chat-page">
        <div className="chat-header">
          <h1>Chat</h1>
          <div className="chat-controls">
            <DocumentSelector collections={collections} documents={documents} value={scope} onChange={setScope} />
            <select className="document-selector" value={answerStyle} onChange={(e) => setAnswerStyle(e.target.value)}>
              {ANSWER_STYLES.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <ChatWindow messages={messages} isAnswering={isAnswering} />

        <form className="chat-input-row" onSubmit={handleSend}>
          <input
            type="text"
            className="chat-input"
            placeholder="Ask a question about your documents..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isAnswering}
          />
          <button type="submit" className="btn-primary" disabled={isAnswering || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </main>
  );
}
