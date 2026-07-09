import { useDispatch, useSelector } from 'react-redux';
import { selectFollowUpActions, selectSuggestedFollowups } from '../../../features/interaction/interactionSelectors';
import { updateFormState } from '../../../features/interaction/interactionSlice';

export default function FollowUpField() {
  const dispatch = useDispatch();
  const followUpActions = useSelector(selectFollowUpActions);
  const suggestedFollowups = useSelector(selectSuggestedFollowups);

  const handleAddFollowUp = (item) => {
    const currentActions = followUpActions ? followUpActions.trim() : '';
    const newActions = currentActions ? `${currentActions}\n- ${item}` : `- ${item}`;

    dispatch(updateFormState({
      follow_up_actions: newActions,
      suggested_followups: suggestedFollowups.filter((f) => f !== item),
    }));
  };

  return (
    <div className="field-group">
      <label className="field-label" htmlFor="follow-up-actions">Follow-up Actions</label>
      <textarea
        id="follow-up-actions"
        className="field-textarea"
        value={followUpActions}
        readOnly
        placeholder="Enter next steps or tasks..."
        rows={2}
      />

      {suggestedFollowups.length > 0 && (
        <div className="suggested-followups">
          <span className="suggested-label">AI Suggested Follow-ups:</span>
          <ul className="suggested-list">
            {suggestedFollowups.map((item, idx) => (
              <li
                key={idx}
                className="suggested-item"
                onClick={() => handleAddFollowUp(item)}
              >
                <span className="suggested-icon">+</span>
                <span className="suggested-text">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

