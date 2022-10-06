export const PageNames = {
  ROOT: 'ROOT',
  TOPICS_ROOT: 'TOPICS_ROOT',
  TOPICS_CHANNEL: 'TOPICS_CHANNEL',
  TOPICS_TOPIC: 'TOPICS_TOPIC',
  TOPICS_CONTENT: 'TOPICS_CONTENT',
  RECOMMENDED: 'RECOMMENDED',
  RECOMMENDED_POPULAR: 'RECOMMENDED_POPULAR',
  RECOMMENDED_RESUME: 'RECOMMENDED_RESUME',
  RECOMMENDED_NEXT_STEPS: 'RECOMMENDED_NEXT_STEPS',
  CONTENT_UNAVAILABLE: 'CONTENT_UNAVAILABLE',
  SEARCH: 'SEARCH',
  EXAM_LIST: 'EXAM_LIST',
  EXAM: 'EXAM',
  EXAM_ROOT: 'EXAM_ROOT',
  KNOWLEDGE_MAP: 'KNOWLEDGE_MAP',
  EDULUTION_TOPICS_ROOT: 'EDULUTION_TOPICS_ROOT',
};

// switch between modes
export const PageModes = {
  TOPICS: 'TOPICS',
  RECOMMENDED: 'RECOMMENDED',
  SEARCH: 'SEARCH',
  EXAM: 'EXAM',
};

export const RecommendedPages = [
  PageNames.RECOMMENDED_POPULAR,
  PageNames.RECOMMENDED_RESUME,
  PageNames.RECOMMENDED_NEXT_STEPS,
];

export const ClassesPageNames = {
  ALL_CLASSES: 'ALL_CLASSES',
  CLASS_ASSIGNMENTS: 'CLASS_ASSIGNMENTS',
  LESSON_PLAYLIST: 'LESSON_PLAYLIST',
  EXAM_VIEWER: 'EXAM_VIEWER',
  EXAM_REPORT_VIEWER: 'EXAM_REPORT_VIEWER',
  LESSON_RESOURCE_VIEWER: 'LESSON_RESOURCE_VIEWER',
};

export const pageNameToModuleMap = {
  [ClassesPageNames.ALL_CLASSES]: 'classes',
  [ClassesPageNames.CLASS_ASSIGNMENTS]: 'classAssignments',
  [ClassesPageNames.EXAM_VIEWER]: 'examViewer',
  [ClassesPageNames.EXAM_REPORT_VIEWER]: 'examReportViewer',
  [ClassesPageNames.LESSON_PLAYLIST]: 'lessonPlaylist',
  [ClassesPageNames.LESSON_RESOURCE_VIEWER]: 'lessonPlaylist/resource',
  [PageNames.TOPICS_ROOT]: 'topicsRoot',
  [PageNames.RECOMMENDED]: 'recommended',
  [PageNames.RECOMMENDED_POPULAR]: 'recommended/subpage',
  [PageNames.RECOMMENDED_RESUME]: 'recommended/subpage',
  [PageNames.RECOMMENDED_NEXT_STEPS]: 'recommended/subpage',
  [PageNames.TOPICS_CHANNEL]: 'topicsTree',
  [PageNames.TOPICS_CONTENT]: 'topicsTree',
  [PageNames.TOPICS_TOPIC]: 'topicsTree',
  [PageNames.RECOMMENDED_CONTENT]: 'topicsTree',
  [PageNames.KNOWLEDGE_MAP]: 'topicsTree',
  [PageNames.EDULUTION_TOPICS_ROOT]: 'topicsRoot',
};

export const prefixToColourMap = {
  'pre-': {
    light: '#D1DDE6',
    dark: '#0072CE',
    accent: '#6CACE4',

    /*original
/*    light: '#D7CCC8',
    dark: '#5D4037',
    accent: '#795548',*/
  },
  alpha: {
    light: '#D4EBBE',
    dark: '#509E2F',
    accent: '#84BD00',

    /*original*/
    /*    light: '#C8E6C9',
    dark: '#388E3C',
    accent: '#4CAF50',*/
  },
  bravo: {
    light: '#E0DBE3',
    dark: '#440099',
    accent: '#7474C1',

    /*original
    light: '#C5CAE9',
    dark: '#303F9F',
    accent: '#3F51B5',*/
  },

  charlie: {
    light: '#F9E547',
    dark: '#FFA300',
    accent: '#FFC72C',

    /*original
    light: '#F8BBD0',
    dark: '#C2185B',
    accent: '#E91E63',*/
  },

  delta: {
    light: '#BBDDE6',
    dark: '#004B87',
    accent: '#005EB8',

    /*original
    light: '#F8BBD0',
    dark: '#C2185B',
    accent: '#E91E63',*/
  },
  /*colors for new courses*/
  'level 1': {
    light: '#D1DDE6',
    dark: '#0072CE',
    accent: '#6CACE4',
  },
  'level 2': {
    light: '#D4EBBE',
    dark: '#509E2F',
    accent: '#84BD00',
  },
  'level 3': {
    light: '#E0DBE3',
    dark: '#440099',
    accent: '#7474C1',
  },

  'level 4': {
    light: '#BBDDE6',
    dark: '#004B87',
    accent: '#005EB8',
  },
  'level 5': {
    light: '#F9E547',
    dark: '#FFA300',
    accent: '#FFC72C',
  },
};
