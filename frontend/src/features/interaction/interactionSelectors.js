/**
 * Memoized selectors for the interaction slice.
 * Components import these instead of reaching into state directly.
 */

export const selectInteraction = (state) => state.interaction;
export const selectHcpName = (state) => state.interaction.hcp_name;
export const selectInteractionType = (state) => state.interaction.interaction_type;
export const selectDate = (state) => state.interaction.date;
export const selectTime = (state) => state.interaction.time;
export const selectAttendees = (state) => state.interaction.attendees;
export const selectTopicsDiscussed = (state) => state.interaction.topics_discussed;
export const selectMaterialsShared = (state) => state.interaction.materials_shared;
export const selectSamplesDistributed = (state) => state.interaction.samples_distributed;
export const selectSentiment = (state) => state.interaction.sentiment;
export const selectOutcomes = (state) => state.interaction.outcomes;
export const selectFollowUpActions = (state) => state.interaction.follow_up_actions;
export const selectSuggestedFollowups = (state) => state.interaction.suggested_followups;
