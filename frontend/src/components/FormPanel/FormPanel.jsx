import HCPField from './fields/HCPField';
import InteractionTypeField from './fields/InteractionTypeField';
import DateTimeField from './fields/DateTimeField';
import AttendeesField from './fields/AttendeesField';
import TopicsField from './fields/TopicsField';
import MaterialsField from './fields/MaterialsField';
import SamplesField from './fields/SamplesField';
import SentimentField from './fields/SentimentField';
import OutcomesField from './fields/OutcomesField';
import FollowUpField from './fields/FollowUpField';

export default function FormPanel() {
  return (
    <div className="form-panel">
      <h1 className="form-title">Log HCP Interaction</h1>

      <div className="form-section">
        <h2 className="section-title">Interaction Details</h2>
        
        <div className="field-row">
          <HCPField />
          <InteractionTypeField />
        </div>

        <DateTimeField />

        <AttendeesField />

        <TopicsField />

        <div className="divider" />

        <div className="materials-section">
          <h3 className="subsection-title">Materials Shared / Samples Distributed</h3>
          <MaterialsField />
          <SamplesField />
        </div>

        <div className="divider" />

        <SentimentField />

        <OutcomesField />

        <FollowUpField />
      </div>
    </div>
  );
}
