import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  hcp_name: '',
  interaction_type: 'Meeting',
  date: '',
  time: '',
  attendees: [],
  topics_discussed: '',
  materials_shared: [],
  samples_distributed: [],
  sentiment: 'Neutral',
  outcomes: '',
  follow_up_actions: '',
  suggested_followups: [],
};

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    /**
     * Merge updated fields into the form state.
     * This is the single reducer the WebSocket result handler calls —
     * state = {...state, ...action.payload}
     */
    updateFormState: (state, action) => {
      const updates = action.payload;
      Object.keys(updates).forEach((key) => {
        if (key in state) {
          state[key] = updates[key];
        }
      });
    },

    /** Replace suggested follow-ups (from the suggest_followups tool). */
    setSuggestedFollowups: (state, action) => {
      state.suggested_followups = action.payload;
    },

    /** Reset form to initial empty state. */
    resetForm: () => initialState,
  },
});

export const { updateFormState, setSuggestedFollowups, resetForm } =
  interactionSlice.actions;

export default interactionSlice.reducer;
