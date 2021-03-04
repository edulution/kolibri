import {
  PageNames as LearnPageNames,
  PageModes as LearnPageModes,
  RecommendedPages as LearnRecommendedPage,
  ClassesPageNames as LearnClassesPageNames,
  pageNameToModuleMap as learnPageNameToModuleMap,
} from '../../../learn/assets/src/constants';

export const PageNames = {
  ...LearnPageNames,
  KNOWLEDGE_MAP: 'KNOWLEDGE_MAP',
  EDULUTION_TOPICS_ROOT: 'EDULUTION_TOPICS_ROOT',
};

export const PageModes = LearnPageModes;

export const RecommendedPages = LearnRecommendedPage;

export const ClassesPageNames = LearnClassesPageNames;

export const pageNameToModuleMap = {
  ...learnPageNameToModuleMap,
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
