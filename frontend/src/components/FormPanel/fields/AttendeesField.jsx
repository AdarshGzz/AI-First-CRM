import { useSelector } from 'react-redux';
import { selectAttendees } from '../../../features/interaction/interactionSelectors';

export default function AttendeesField() {
  const attendees = useSelector(selectAttendees);

  return (
    <div className="field-group">
      <label className="field-label" htmlFor="attendees">Attendees</label>
      <div className="tags-input" id="attendees">
        {attendees.length > 0 ? (
          <div className="tags-list">
            {attendees.map((name, idx) => (
              <span key={idx} className="tag">
                {name}
              </span>
            ))}
          </div>
        ) : (
          <span className="tags-placeholder">Enter names or search...</span>
        )}
      </div>
    </div>
  );
}
