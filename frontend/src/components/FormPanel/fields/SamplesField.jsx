import { useSelector } from 'react-redux';
import { selectSamplesDistributed } from '../../../features/interaction/interactionSelectors';

export default function SamplesField() {
  const samples = useSelector(selectSamplesDistributed);

  return (
    <div className="field-group">
      <div className="field-header-row">
        <label className="field-label">Samples Distributed</label>
        <button className="action-btn" type="button" disabled>
          <span>💊</span> Add Sample
        </button>
      </div>
      <div className="items-list">
        {samples.length > 0 ? (
          samples.map((item, idx) => (
            <span key={idx} className="item-chip">{item}</span>
          ))
        ) : (
          <span className="items-empty">No samples added.</span>
        )}
      </div>
    </div>
  );
}
