import { get } from '@vueuse/core';
import store from 'kolibri.coreVue.vuex.store';
import router from 'kolibri.coreVue.router';
import { ClassesPageNames, PageNames } from '../constants';
import { showLessonPlaylist } from '../modules/lessonPlaylist/handlers';
import { showClassAssignmentsPage } from '../modules/classAssignments/handlers';
import { showAllClassesPage } from '../modules/classes/handlers';
import { showExam, showAssessment } from '../modules/examViewer/handlers';
import { showExamReport, showAssessmentReport } from '../modules/examReportViewer/handlers';
import { inClasses } from '../composables/useCoreLearn';
import ExamPage from '../views/ExamPage';
import ExamReportViewer from '../views/LearnExamReportViewer';
import AllClassesPage from '../views/classes/AllClassesPage';
import ClassAssignmentsPage from '../views/classes/ClassAssignmentsPage';
import LessonPlaylistPage from '../views/classes/LessonPlaylistPage';
import AssessmentPage from '../views/AssessmentPage';
import AssessmentReportViewer from '../views/LearnAssessmentReportViewer';

function noClassesGuard() {
  const { canAccessUnassignedContent } = store.getters;
  if (!get(inClasses) && canAccessUnassignedContent) {
    // If there are no memberships and it is allowed, redirect to library page
    return router.replace({ name: PageNames.LIBRARY });
  }
  // Otherwise return nothing
  return;
}

export default [
  {
    name: ClassesPageNames.ALL_CLASSES,
    path: '/classes',
    handler: () => {
      return noClassesGuard() || showAllClassesPage(store);
    },
    component: AllClassesPage,
  },
  {
    name: ClassesPageNames.CLASS_ASSIGNMENTS,
    path: '/classes/:classId',
    handler: toRoute => {
      const { classId } = toRoute.params;
      return noClassesGuard() || showClassAssignmentsPage(store, classId);
    },
    component: ClassAssignmentsPage,
  },
  {
    name: ClassesPageNames.LESSON_PLAYLIST,
    path: '/classes/:classId/lesson/:lessonId',
    handler: toRoute => {
      const { classId, lessonId } = toRoute.params;
      return noClassesGuard() || showLessonPlaylist(store, { classId, lessonId });
    },
    component: LessonPlaylistPage,
  },
  {
    name: ClassesPageNames.EXAM_VIEWER,
    path: '/classes/:classId/exam/:examId/:questionNumber',
    handler: (toRoute, fromRoute) => {
      if (noClassesGuard()) {
        return noClassesGuard();
      }
      const alreadyOnQuiz =
        fromRoute.name === ClassesPageNames.EXAM_VIEWER &&
        toRoute.params.examId === fromRoute.params.examId &&
        toRoute.params.classId === fromRoute.params.classId;
      showExam(store, toRoute.params, alreadyOnQuiz);
    },
    component: ExamPage,
  },
  {
    name: ClassesPageNames.EXAM_REPORT_VIEWER,
    path: '/classes/:classId/examReport/:examId/:tryIndex/:questionNumber/:questionInteraction',
    handler: toRoute => {
      if (noClassesGuard()) {
        return noClassesGuard();
      }
      showExamReport(store, toRoute.params);
    },
    component: ExamReportViewer,
  },
  {
    name: ClassesPageNames.ASSESSMENT_VIEWER,
    path: '/classes/:classId/assessment/:examId/:questionNumber',
    handler: (toRoute, fromRoute) => {
      if (noClassesGuard()) {
        return noClassesGuard();
      }
      const alreadyOnAssessment =
        fromRoute.name === ClassesPageNames.ASSESSMENT_VIEWER &&
        toRoute.params.examId === fromRoute.params.examId &&
        toRoute.params.classId === fromRoute.params.classId;
        showAssessment(store, toRoute.params, alreadyOnAssessment);
    },
    component: AssessmentPage,
  },
  {
    name: ClassesPageNames.ASSESSMENT_REPORT_VIEWER,
    path: '/classes/:classId/assessmentReport/:examId/:tryIndex/:questionNumber/:questionInteraction',
    handler: toRoute => {
      if (noClassesGuard()) {
        return noClassesGuard();
      }
      showAssessmentReport(store, toRoute.params);
    },
    component: AssessmentReportViewer,
  },
];
