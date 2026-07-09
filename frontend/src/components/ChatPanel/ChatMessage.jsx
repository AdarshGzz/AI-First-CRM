export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const isToken = message.type === 'token';

  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'} ${isToken ? 'token' : ''}`}>
      {!isUser && (
        <div className="message-avatar">
          <span className="avatar-icon">🤖</span>
        </div>
      )}
      <div className={`message-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}`}>
        <div className="message-content">
          {message.content.split('\n').map((line, i) => (
            <span key={i}>
              {line}
              {i < message.content.split('\n').length - 1 && <br />}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
