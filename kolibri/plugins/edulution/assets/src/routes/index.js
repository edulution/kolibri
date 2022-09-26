import store from 'kolibri.coreVue.vuex.store';
import router from 'kolibri.coreVue.router';
import { showKnowledgeMap } from '../modules/topicsTree/handlers';
import { PageNames } from '../constants';
import routes from '../../../../learn/assets/src/routes';
import { showChannels } from '../modules/topicsRoot/handlers';

export default [
  /*Override the
default root page.Default to the page that shows the channels a user has access to
*/
  {
    name: PageNames.ROOT,
    path: '/',
    handler: () => {
      return router.replace({
        name: PageNames.EDULUTION_TOPICS_ROOT,
      });
      showChannels(store);
    },
  },
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
  ...routes,
];
