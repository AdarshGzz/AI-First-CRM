import { useSelector } from 'react-redux';
import { selectSentiment } from '../../../features/interaction/interactionSelectors';

const SENTIMENTS = [
  { value: 'Positive', emoji: '😊', color: '#22c55e' },
  { value: 'Neutral', emoji: '😐', color: '#f59e0b' },
  { value: 'Negative', emoji: '😟', color: '#ef4444' },
];

export default function SentimentField() {
  const sentiment = useSelector(selectSentiment);

  return (
    <div className="field-group">
      <label className="field-label">Observed/Inferred HCP Sentiment</label>
      <div className="sentiment-options">
        {SENTIMENTS.map((s) => (
          <label
            key={s.value}
            className={`sentiment-option ${sentiment === s.value ? 'active' : ''}`}
          >
            <input
              type="radio"
              name="sentiment"
              value={s.value}
              checked={sentiment === s.value}
              readOnly
              disabled
            />
            <span className="sentiment-radio" style={{ borderColor: sentiment === s.value ? s.color : undefined }}>
              {sentiment === s.value && (
                <span className="sentiment-dot" style={{ backgroundColor: s.color }} />
              )}
            </span>
            <span className="sentiment-emoji">{s.emoji}</span>
            <span className="sentiment-label">{s.value}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
