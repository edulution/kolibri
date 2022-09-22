import { PageNames, PageModes } from '../../constants';

function _learnPageMode(state) {
  const topicsPages = [
    PageNames.TOPICS_ROOT,
    PageNames.TOPICS_CHANNEL,
    PageNames.TOPICS_TOPIC,
    PageNames.TOPICS_CONTENT,
  ];
  const examPages = [PageNames.EXAM_LIST, PageNames.EXAM];
  const pageNameMatches = page => page === state.pageName;
  if (topicsPages.some(pageNameMatches)) {
    return PageModes.TOPICS;
  } else if (PageNames.RECOMMENDED === state.pageName) {
    return PageModes.RECOMMENDED;
  } else if (PageNames.SEARCH === state.pageName) {
    return PageModes.SEARCH;
  } else if (examPages.some(pageNameMatches)) {
    return PageModes.EXAM;
  }
  return undefined;
}
export function pageMode(state) {
  const mode = _learnPageMode(state);
  return mode === undefined && state.pageName === PageNames.KNOWLEDGE_MAP ? PageModes.TOPICS : mode;
}
