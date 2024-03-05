function defaultState() {
  return {
    contentNodeMap: {},
    exam: {},
    questionNumber: 0,
    questions: [],
    knowledgemap: {},
  };
}

export default {
  namespaced: true,
  state: defaultState(),
  mutations: {
    SET_STATE(state, payload) {
      Object.assign(state, payload);
    },
    RESET_STATE(state) {
      Object.assign(state, defaultState());
    },
  },
};
