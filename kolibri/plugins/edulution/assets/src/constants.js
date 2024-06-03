import plugin_data from 'plugin_data';

// a name for every URL pattern
export const PageNames = {
  ROOT: 'ROOT',
  HOME: 'HOME',
  TOPICS_TOPIC: 'TOPICS_TOPIC',
  TOPICS_TOPIC_SEARCH: 'TOPICS_TOPIC_SEARCH',
  TOPICS_CONTENT: 'TOPICS_CONTENT',
  LIBRARY: 'LIBRARY',
  CONTENT_UNAVAILABLE: 'CONTENT_UNAVAILABLE',
  EXAM_LIST: 'EXAM_LIST',
  EXAM: 'EXAM',
  EXAM_ROOT: 'EXAM_ROOT',
  BOOKMARKS: 'BOOKMARKS',
  EXPLORE_LIBRARIES: 'EXPLORE_LIBRARIES',
  ASSESSMENT_HISTORY: 'ASSESSMENT_HISTORY'
};

export const ExternalPageNames = {
  MY_DOWNLOADS: 'MY_DOWNLOADS',
};

export const ExternalPagePaths = {
  [ExternalPageNames.MY_DOWNLOADS]: '/my-downloads',
};

export const ClassesPageNames = {
  ALL_CLASSES: 'ALL_CLASSES',
  CLASS_ASSIGNMENTS: 'CLASS_ASSIGNMENTS',
  LESSON_PLAYLIST: 'LESSON_PLAYLIST',
  CLASS_LEARNERS_LIST_VIEWER: 'CLASS_LEARNERS_LIST_VIEWER',
  EXAM_VIEWER: 'EXAM_VIEWER',
  EXAM_REPORT_VIEWER: 'EXAM_REPORT_VIEWER',
  ASSESSMENT_VIEWER: 'ASSESSMENT_VIEWER',
  ASSESSMENT_REPORT_VIEWER: 'ASSESSMENT_REPORT_VIEWER',
};

export const pageNameToModuleMap = {
  [ClassesPageNames.ALL_CLASSES]: 'classes',
  [ClassesPageNames.CLASS_ASSIGNMENTS]: 'classAssignments',
  [ClassesPageNames.EXAM_VIEWER]: 'examViewer',
  [ClassesPageNames.EXAM_REPORT_VIEWER]: 'examReportViewer',
  [ClassesPageNames.LESSON_PLAYLIST]: 'lessonPlaylist',
};

export const KolibriStudioId = plugin_data.studioDevice?.instance_id;

export const channelThemeTokens = {
  default: {
    primary: '#071d49',
    primaryDark: '#071d49',
    appBar: '#071d49',
    appBarDark: '#071d49',
    link: '#071d49',
    linkDark: '#071d49',
  },
  /*colors for new courses*/
  level1: {
    primary: '#0072CE',
    primaryDark: '#0072CE',
    appBar: '#0072CE',
    appBarDark: '#0072CE',
    link: '#0072CE',
    linkDark: '#0072CE',
  },
  level2: {
    primary: '#509E2F',
    primaryDark: '#509E2F',
    appBar: '#509E2F',
    appBarDark: '#509E2F',
    link: '#509E2F',
    linkDark: '#509E2F',
  },
  level3: {
    primary: '#440099',
    primaryDark: '#440099',
    appBar: '#440099',
    appBarDark: '#440099',
    link: '#440099',
    linkDark: '#440099',
  },
  level4: {
    primary: '#004B87',
    primaryDark: '#004B87',
    appBar: '#004B87',
    appBarDark: '#004B87',
    link: '#004B87',
    linkDark: '#004B87',
  },
  level5: {
    primary: '#FFA300',
    primaryDark: '#FFA300',
    appBar: '#FFA300',
    appBarDark: '#FFA300',
    link: '#FFA300',
    linkDark: '#FFA300',
  },
  level6: {
    primary: '#071d49',
    primaryDark: '#071d49',
    appBar: '#071d49',
    appBarDark: '#071d49',
    link: '#071d49',
    linkDark: '#071d49',
  },
  level7: {
    primary: '#071d49',
    primaryDark: '#071d49',
    appBar: '#071d49',
    appBarDark: '#071d49',
    link: '#071d49',
    linkDark: '#071d49',
  },
}