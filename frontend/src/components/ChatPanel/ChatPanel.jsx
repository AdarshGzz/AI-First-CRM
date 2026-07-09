import { useState, useEffect, useRef, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { selectInteraction } from '../../features/interaction/interactionSelectors';
import { updateFormState, setSuggestedFollowups } from '../../features/interaction/interactionSlice';
import chatApi from '../../api/chatApi';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

const INITIAL_MESSAGE = {
  role: 'assistant',
  type: 'result',
  content:
    'Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure") or ask for help.',
};

export default function ChatPanel() {
  const dispatch = useDispatch();
  const formState = useSelector(selectInteraction);
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [status, setStatus] = useState('disconnected');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle incoming WebSocket messages
  const handleMessage = useCallback(
    (data) => {
      if (data.type === 'token') {
        // Show a processing indicator message (replace previous token)
        setMessages((prev) => {
          const filtered = prev.filter((m) => m.type !== 'token');
          return [...filtered, { role: 'assistant', type: 'token', content: data.content }];
        });
      } else if (data.type === 'result') {
        setIsProcessing(false);

        // Remove token messages
        setMessages((prev) => {
          const filtered = prev.filter((m) => m.type !== 'token');
          return [
            ...filtered,
            { role: 'assistant', type: 'result', content: data.chat_reply || 'Done.' },
          ];
        });

        // Update Redux form state with the tool result
        if (data.updated_state && Object.keys(data.updated_state).length > 0) {
          dispatch(updateFormState(data.updated_state));
        }

        // Handle suggested follow-ups
        if (data.suggested_followups && data.suggested_followups.length > 0) {
          dispatch(setSuggestedFollowups(data.suggested_followups));
        }
      } else if (data.type === 'rate_limited') {
        setIsProcessing(false);
        setMessages((prev) => {
          const filtered = prev.filter((m) => m.type !== 'token');
          return [
            ...filtered,
            {
              role: 'assistant',
              type: 'result',
              content: `⏳ Rate limited. Please wait ${data.retry_after_seconds}s and try again.`,
            },
          ];
        });
      } else if (data.type === 'error') {
        setIsProcessing(false);
        setMessages((prev) => {
          const filtered = prev.filter((m) => m.type !== 'token');
          return [
            ...filtered,
            {
              role: 'assistant',
              type: 'result',
              content: `❌ ${data.message || 'An error occurred.'}`,
            },
          ];
        });
      }
    },
    [dispatch]
  );

  // Connect on mount
  useEffect(() => {
    chatApi.connect(handleMessage, setStatus);
    return () => chatApi.disconnect();
  }, [handleMessage]);

  // Send message handler
  const handleSend = (text) => {
    // Add user message to chat
    setMessages((prev) => [...prev, { role: 'user', type: 'user', content: text }]);
    setIsProcessing(true);

    // Send via WebSocket with current Redux state
    const sent = chatApi.sendMessage(text, formState);
    if (!sent) {
      setIsProcessing(false);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          type: 'result',
          content: '⚠️ Not connected to server. Please wait for reconnection.',
        },
      ]);
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-left">
          <span className="chat-header-icon">🤖</span>
          <div>
            <h2 className="chat-header-title">AI Assistant</h2>
            <p className="chat-header-subtitle">Log interaction via chat</p>
          </div>
        </div>
        <div className={`connection-status ${status}`}>
          <span className="status-dot" />
          <span className="status-text">{status}</span>
        </div>
      </div>

      <div className="chat-messages" id="chat-messages">
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} message={msg} />
        ))}
        {isProcessing && (
          <div className="chat-message assistant">
            <div className="message-avatar">
              <span className="avatar-icon">🤖</span>
            </div>
            <div className="message-bubble assistant-bubble">
              <div className="typing-indicator">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSend={handleSend} disabled={isProcessing || status === 'failed'} />
    </div>
  );
}
