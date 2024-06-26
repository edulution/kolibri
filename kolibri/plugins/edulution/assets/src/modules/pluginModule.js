import * as getters from './coreLearn/getters';
import topicsTree from './topicsTree';
import mutations from './coreLearn/mutations';
import * as actions from './coreLearn/actions';
import classAssignments from './classAssignments';
import classes from './classes';
import examReportViewer from './examReportViewer';
import examViewer from './examViewer';
import lessonPlaylist from './lessonPlaylist';
import recommended from './recommended';
import search from './search';
import topicsRoot from './topicsRoot';

export default {
  state: {
    pageName: '',
    examAttemptLogs: {},
    examLog: {},
    memberships: [],
  },
  actions,
  getters,
  mutations,
  modules: {
    classAssignments,
    classes,
    examReportViewer,
    examViewer,
    lessonPlaylist,
    recommended,
    search,
    topicsRoot,
    topicsTree,
  },
};
