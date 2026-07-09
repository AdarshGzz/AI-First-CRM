import { useSelector } from 'react-redux';
import { selectHcpName } from '../../../features/interaction/interactionSelectors';

export default function HCPField() {
  const hcpName = useSelector(selectHcpName);

  return (
    <div className="field-group">
      <label className="field-label" htmlFor="hcp-name">HCP Name</label>
      <input
        id="hcp-name"
        type="text"
        className="field-input"
        value={hcpName}
        readOnly
        placeholder="Search or select HCP..."
      />
    </div>
  );
}
