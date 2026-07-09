import { useSelector } from 'react-redux';
import { selectTopicsDiscussed } from '../../../features/interaction/interactionSelectors';

export default function TopicsField() {
  const topics = useSelector(selectTopicsDiscussed);

  return (
    <div className="field-group">
      <label className="field-label" htmlFor="topics-discussed">Topics Discussed</label>
      <textarea
        id="topics-discussed"
        className="field-textarea"
        value={topics}
        readOnly
        placeholder="Enter key discussion points..."
        rows={3}
      />
      <button className="voice-btn" type="button" disabled>
        <span className="voice-icon">✨</span>
        Summarize from Voice Note (Requires Consent)
      </button>
    </div>
  );
}
