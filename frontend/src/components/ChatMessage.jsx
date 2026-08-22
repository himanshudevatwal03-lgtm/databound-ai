import AnswerCard from "./AnswerCard.jsx";

/**
 * ChatMessage
 *
 * One turn in the conversation. User questions render as a simple
 * right-aligned bubble; AI answers render as a full AnswerCard with the
 * supported/unsupported badge and citations. Kept as its own component
 * (rather than inlining both cases in ChatWindow) so Phase 7's real
 * conversation history can reuse it unchanged.
 */
export default function ChatMessage({ message }) {
  if (message.role === "user") {
    return (
      <div className="chat-message chat-message-user">
        <div className="chat-bubble-user">{message.text}</div>
      </div>
    );
  }

  if (message.role === "error") {
    return (
      <div className="chat-message chat-message-assistant">
        <div className="chat-bubble-error">{message.text}</div>
      </div>
    );
  }

  return (
    <div className="chat-message chat-message-assistant">
      <AnswerCard answer={message.answer} supported={message.supported} sources={message.sources} />
    </div>
  );
}
