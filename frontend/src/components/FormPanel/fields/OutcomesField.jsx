import { useSelector } from 'react-redux';
import { selectOutcomes } from '../../../features/interaction/interactionSelectors';

export default function OutcomesField() {
  const outcomes = useSelector(selectOutcomes);

  return (
    <div className="field-group">
      <label className="field-label" htmlFor="outcomes">Outcomes</label>
      <textarea
        id="outcomes"
        className="field-textarea"
        value={outcomes}
        readOnly
        placeholder="Key outcomes or agreements..."
        rows={2}
      />
    </div>
  );
}
