import { useSelector } from 'react-redux';
import { selectDate, selectTime } from '../../../features/interaction/interactionSelectors';

export default function DateTimeField() {
  const date = useSelector(selectDate);
  const time = useSelector(selectTime);

  return (
    <div className="field-row">
      <div className="field-group">
        <label className="field-label" htmlFor="interaction-date">Date</label>
        <div className="input-icon-wrapper">
          <input
            id="interaction-date"
            type="text"
            className="field-input"
            value={date}
            readOnly
            placeholder="DD-MM-YYYY"
          />
          <span className="input-icon">📅</span>
        </div>
      </div>
      <div className="field-group">
        <label className="field-label" htmlFor="interaction-time">Time</label>
        <div className="input-icon-wrapper">
          <input
            id="interaction-time"
            type="text"
            className="field-input"
            value={time}
            readOnly
            placeholder="HH:MM"
          />
          <span className="input-icon">🕐</span>
        </div>
      </div>
    </div>
  );
}
