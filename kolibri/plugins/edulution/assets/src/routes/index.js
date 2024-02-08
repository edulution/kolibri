import store from 'kolibri.coreVue.vuex.store';
import router from 'kolibri.coreVue.router';
import { PageNames, ClassesPageNames } from '../constants';
import { showChannels } from '../modules/topicsRoot/handlers';
import { showSearch } from '../modules/search/handlers';
import {
  showTopicsTopic,
  showTopicsChannel,
  showTopicsContent,
  showKnowledgeMap,
} from '../modules/topicsTree/handlers';
import {
  showRecommended,
  showPopularPage,
  showNextStepsPage,
  showResumePage,
} from '../modules/recommended/handlers';
import classesRoutes from './classesRoutes';

export default [
  ...classesRoutes,
  {
    name: PageNames.KNOWLEDGE_MAP,
    path: '/topics/t/:id',
    handler: toRoute => {
      showKnowledgeMap(store, toRoute.params.id);
    },
  },
  {
    name: PageNames.EDULUTION_TOPICS_ROOT,
    path: '/topics',
    handler: () => {
      showChannels(store);
    },
  },
  {
    name: PageNames.ROOT,
    path: '/',
    handler: () => {
      const { memberships } = store.state;
      // If a registered user, go to Classes Page, else go to Content
      return router.replace({
        /*name: memberships.length > 0 ? ClassesPageNames.ALL_CLASSES : PageNames.TOPICS_ROOT,*/
        name: PageNames.TOPICS_ROOT,
      });
    },
  },
  {
    name: PageNames.TOPICS_ROOT,
    path: '/topics',
    handler: () => {
      showChannels(store);
    },
  },
  {
    name: PageNames.RECOMMENDED,
    path: '/recommended',
    handler: () => {
      showRecommended(store);
    },
  },
  {
    name: PageNames.SEARCH,
    path: '/search',
    handler: toRoute => {
      showSearch(store, { ...toRoute.query });
    },
  },
  {
    name: PageNames.CONTENT_UNAVAILABLE,
    path: '/content-unavailable',
    handler: () => {
      store.commit('SET_PAGE_NAME', PageNames.CONTENT_UNAVAILABLE);
      store.commit('CORE_SET_PAGE_LOADING', false);
      store.commit('CORE_SET_ERROR', null);
    },
  },
  {
    name: PageNames.TOPICS_CHANNEL,
    path: '/topics/:channel_id',
    handler: toRoute => {
      showTopicsChannel(store, toRoute.params.channel_id);
    },
  },
  {
    name: PageNames.TOPICS_TOPIC,
    path: '/topics/t/:id',
    handler: toRoute => {
      showTopicsTopic(store, { id: toRoute.params.id });
    },
  },
  {
    name: PageNames.TOPICS_CONTENT,
    path: '/topics/c/:id',
    handler: toRoute => {
      showTopicsContent(store, toRoute.params.id);
    },
  },
  {
    name: PageNames.RECOMMENDED_POPULAR,
    path: '/recommended/popular',
    handler: () => {
      showPopularPage(store);
    },
  },
  {
    name: PageNames.RECOMMENDED_RESUME,
    path: '/recommended/resume',
    handler: () => {
      showResumePage(store);
    },
  },
  {
    name: PageNames.RECOMMENDED_NEXT_STEPS,
    path: '/recommended/nextsteps',
    handler: () => {
      showNextStepsPage(store);
    },
  },
  {
    path: '*',
    redirect: '/',
  },
];
