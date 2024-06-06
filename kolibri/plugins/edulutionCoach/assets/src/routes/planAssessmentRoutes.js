import store from 'kolibri.coreVue.vuex.store';
import { PageNames } from '../constants';
import {
  showExamCreationRootPage,
  showExamCreationTopicPage,
  showExamCreationBookmarksPage,
  showExamCreationAllBookmarks,
  showExamCreationSearchPage,
  showExamCreationQuestionSelectionPage,
  showExamCreationPreviewPage,
  showPracticeQuizCreationPreviewPage,
} from '../modules/assessmentCreation/handlers';
import { showExamsPage } from '../modules/examsRoot/handlers';
import CreateAssessmentPage from '../views/plan/CreateAssessmentPage/index.vue';
import CreateAssessmentPreviewPage from '../views/plan/CreateAssessmentPage/CreateAssessmentPreview.vue';
import PlanQuizPreviewPage from '../views/plan/PlanQuizPreviewPage.vue';
import CoachAssessmentsPage from '../views/plan/CoachAssessmentsPage/index.vue';
import AssessmentSummaryPage from '../views/plan/AssessmentSummaryPage/index.vue';
import PlanPracticeQuizPreviewPage from '../views/plan/CreateAssessmentPage/PlanPracticeQuizPreviewPage.vue';

export default [
  {
    name: PageNames.ASSESSMENTS,
    path: '/:classId/plan/assessments',
    component: CoachAssessmentsPage,
    handler(toRoute) {
      showExamsPage(store, toRoute.params.classId);
    },
    meta: {
      titleParts: ['assessmentLabel', 'CLASS_NAME'],
    },
  },
  {
    name: PageNames.ASSESSMENT_CREATION_ROOT,
    path: '/:classId/plan/assessments/new/',
    component: CreateAssessmentPage,
    handler: toRoute => {
      showExamCreationRootPage(store, toRoute.params);
    },
  },
  {
    name: PageNames.ASSESSMENT_CREATION_TOPIC,
    path: '/:classId/plan/assessments/new/topic/:topicId',
    component: CreateAssessmentPage,
    handler: toRoute => {
      showExamCreationTopicPage(store, toRoute.params);
    },
  },
  {
    name: PageNames.ASSESSMENT_CREATION_BOOKMARKS,
    path: '/:classId/plan/assessments/new/bookmark/:topicId',
    component: CreateAssessmentPage,
    handler: toRoute => {
      showExamCreationBookmarksPage(store, toRoute.params);
    },
  },
  {
    name: PageNames.ASSESSMENT_CREATION_BOOKMARKS_MAIN,
    path: '/:classId/plan/assessments/new/bookmarks',
    component: CreateAssessmentPage,
    handler: toRoute => {
      showExamCreationAllBookmarks(store, toRoute.params);
    },
  },
  {
    name: PageNames.ASSESSMENT_CREATION_SEARCH,
    path: '/:classId/plan/assessments/new/search/:searchTerm',
    component: CreateAssessmentPage,
    handler: toRoute => {
      showExamCreationSearchPage(store, toRoute.params, toRoute.query);
    },
  },
  {
    name: PageNames.ASSESSMENT_CREATION_QUESTION_SELECTION,
    path: '/:classId/plan/assessments/new/finalize',
    component: CreateAssessmentPreviewPage,
    handler: (toRoute, fromRoute) => {
      showExamCreationQuestionSelectionPage(store, toRoute, fromRoute);
    },
  },
  {
    name: PageNames.ASSESSMENT_CREATION_PRACTICE_QUIZ_PREVIEW,
    path: '/:classId/plan/assessments/new/practice_assessment/preview/',
    component: PlanPracticeQuizPreviewPage,
    handler: toRoute => {
      showPracticeQuizCreationPreviewPage(store, toRoute.params);
    },
  },
  {
    name: PageNames.ASSESSMENT_CREATION_PREVIEW,
    path: '/:classId/plan/assessments/new/preview/',
    component: PlanQuizPreviewPage,
    handler: (toRoute, fromRoute) => {
      showExamCreationPreviewPage(store, toRoute.params, fromRoute);
    },
  },
  {
    name: PageNames.ASSESSMENT_QUIZ_SUMMARY,
    path: '/:classId/plan/assessments/:assessmentId',
    component: AssessmentSummaryPage,
    meta: {
      titleParts: ['QUIZ_NAME', 'assessmentLabel', 'CLASS_NAME'],
    },
  },
];
