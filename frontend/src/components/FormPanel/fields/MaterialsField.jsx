import { useSelector } from 'react-redux';
import { selectMaterialsShared } from '../../../features/interaction/interactionSelectors';

export default function MaterialsField() {
  const materials = useSelector(selectMaterialsShared);

  return (
    <div className="field-group">
      <div className="field-header-row">
        <label className="field-label">Materials Shared</label>
        <button className="action-btn" type="button" disabled>
          <span>🔍</span> Search/Add
        </button>
      </div>
      <div className="items-list">
        {materials.length > 0 ? (
          materials.map((item, idx) => (
            <span key={idx} className="item-chip">{item}</span>
          ))
        ) : (
          <span className="items-empty">No materials added.</span>
        )}
      </div>
    </div>
  );
}
