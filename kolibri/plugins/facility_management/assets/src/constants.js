export const PageNames = {
  CLASS_MGMT_PAGE: 'CLASS_MGMT_PAGE',
  CLASS_EDIT_MGMT_PAGE: 'CLASS_EDIT_MGMT_PAGE',
  CLASS_ENROLL_LEARNER: 'CLASS_ENROLL_LEARNER',
  CLASS_ASSIGN_COACH: 'CLASS_ASSIGN_COACH',
  USER_MGMT_PAGE: 'USER_MGMT_PAGE',
  DATA_EXPORT_PAGE: 'DATA_EXPORT_PAGE',
  FACILITY_CONFIG_PAGE: 'FACILITY_CONFIG_PAGE',
};

// modal names
export const Modals = {
  CREATE_CLASS: 'CREATE_CLASS',
  DELETE_CLASS: 'DELETE_CLASS',
  EDIT_CLASS_NAME: 'EDIT_CLASS_NAME',
  REMOVE_USER: 'REMOVE_USER',
  CONFIRM_ENROLLMENT: 'CONFIRM_ENROLLMENT',
  CREATE_USER: 'CREATE_USER',
  EDIT_USER: 'EDIT_USER',
  RESET_USER_PASSWORD: 'RESET_USER_PASSWORD',
  DELETE_USER: 'DELETE_USER',
};

export const defaultFacilityConfig = {
  learnerCanEditUsername: true,
  learnerCanEditName: true,
  learnerCanEditPassword: true,
  learnerCanEditGender: true,
  learnerCanEditBirthYear: true,
  learnerCanEditExamNumber: true,
  learnerCanSignUp: true,
  learnerCanDeleteAccount: true,
  learnerCanLoginWithNoPassword: false,
  showDownloadButtonInLearn: false,
  allowGuestAccess: true,
  learnerCanViewLessons: false,
};

export const notificationTypes = {
  PAGELOAD_FAILURE: 'PAGELOAD_FAILURE',
  SAVE_FAILURE: 'SAVE_FAILURE',
  SAVE_SUCCESS: 'SAVE_SUCCESS',
};

export const pageNameToModuleMap = {
  [PageNames.CLASS_MGMT_PAGE]: 'classManagement',
  [PageNames.CLASS_EDIT_MGMT_PAGE]: 'classEditManagement',
  [PageNames.CLASS_ASSIGN_COACH]: 'classAssignMembers',
  [PageNames.CLASS_ENROLL_LEARNER]: 'classAssignMembers',
  [PageNames.USER_MGMT_PAGE]: 'userManagement',
  [PageNames.FACILITY_CONFIG_PAGE]: 'facilityConfig',
};

export const TaskTypes = {
  EXPORTSESSIONLOGCSV: 'EXPORTSESSIONLOGCSV',
  EXPORTSUMMARYLOGCSV: 'EXPORTSUMMARYLOGCSV',
};

export const TaskStatuses = {
  IN_PROGRESS: 'INPROGRESS',
  COMPLETED: 'COMPLETED',
  FAILED: 'FAILED',
  PENDING: 'PENDING',
  RUNNING: 'RUNNING',
  QUEUED: 'QUEUED',
  SCHEDULED: 'SCHEDULED',
};

export const CSVGenerationStatuses = {
  NO_LOGS_CREATED: 'NOLOGSCREATED',
  GENERATING: 'GENERATING',
  AVAILABLE: 'AVAILABLE',
};
