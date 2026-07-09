import { useSelector } from 'react-redux';
import { selectInteractionType } from '../../../features/interaction/interactionSelectors';

const TYPES = ['Meeting', 'Call', 'Email', 'Video Call', 'Conference'];

export default function InteractionTypeField() {
  const interactionType = useSelector(selectInteractionType);

  return (
    <div className="field-group">
      <label className="field-label" htmlFor="interaction-type">Interaction Type</label>
      <div className="select-wrapper">
        <select
          id="interaction-type"
          className="field-select"
          value={interactionType}
          disabled
        >
          {TYPES.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
        <span className="select-chevron">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </span>
      </div>
    </div>
  );
}
