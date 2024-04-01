<template>

  <CoachAppBarPage
    :authorized="$store.getters.userIsAuthorizedForCoach"
    authorizedRole="adminOrCoach"
    :showSubNav="true"
  >

    <KGrid gutter="16">
      <KGridItem>
        <AssessmentLessonDetailsHeader
          :backlink="$router.getRoute('ASSESSMENTS')"
          :backlinkLabel="coachString('allAssessmentsLabel')"
          examOrLesson="exam"
          :assessmentTitle="quiz.title"
        />

      </KGridItem>

      <KGridItem :layout12="{ span: 4 }">
        <h2 class="visuallyhidden">
          {{ coachString('generalInformationLabel') }}
        </h2>
        <AssessmentStatus
          :className="className"
          :avgScore="avgScore"
          :groupAndAdHocLearnerNames="getRecipientNamesForExam(exam)"
          :exam="exam"
        />
      </KGridItem>
      
      <KGridItem :layout12="{ span: 8 }">
        <KPageContainer
          v-if="!loading"
          :topMargin="16"
        >
          <section v-if="currentView === 'TEST_LISTING'">
            <CoreTable :emptyMessage="coachString('learnerListEmptyState')">
              <template #headers>
                <th>{{ coachString('topicLabel') }}</th>
              </template>
              <template #tbody>
                <transition-group tag="tbody" name="list">
                  <tr v-for="tableRow of assessmentList" :key="tableRow.id" data-test="entry">
                    <KLabeledIcon
                      :icon="'quiz'"
                      :label="tableRow.title " 
                      class="table-title"
                      @click.prevent="toggleView('QUESTION_PREVIEW')"
                    />
                  </tr>
                </transition-group>
              </template>
            </CoreTable>
          </section>  
          
          <section v-if="currentView === 'QUESTION_PREVIEW'">
            <div  
              class="back-arrow"
              @click.prevent="toggleView('TEST_LISTING')"
            >
              <KIcon
                icon="back"
              />
              <span>Back To Listing</span>
            </div>

            <h2>
              {{ coachString('numberOfQuestions', { value: selectedQuestions.length }) }}
            </h2>

            <p>
              {{ orderDescriptionString }}
            </p>

            <QuestionListPreview
              :fixedOrder="!quizIsRandomized"
              :readOnly="true"
              :selectedQuestions="selectedQuestions"
              :selectedExercises="selectedExercises"
            />
          </section>
        </KPageContainer>
      </KGridItem>
    </KGrid>

    <ManageExamModals
      :currentAction="currentAction"
      :quiz="quiz"
      @submit_delete="handleSubmitDelete"
      @submit_copy="handleSubmitCopy"
      @cancel="closeModal"
    />
  </CoachAppBarPage>

</template>


<script>
  import { AssessmentGroupDataResource } from 'kolibri.resources';
  import { mapState } from 'vuex';
  import fromPairs from 'lodash/fromPairs';
  import find from 'lodash/find';
  import { ERROR_CONSTANTS } from 'kolibri.coreVue.vuex.constants';
  import CatchErrors from 'kolibri.utils.CatchErrors';
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import commonCoach from '../../common';
  import CoachAppBarPage from '../../CoachAppBarPage';
  import QuestionListPreview from '../CreateExamPage/QuestionListPreview';
  import { coachStringsMixin } from '../../common/commonCoachStrings';
  import ManageExamModals from './ManageExamModals';
  import {
    fetchAssessmentSummaryPageData,
    serverAssignmentPayload,
    clientAssigmentState,
    deleteExam,
  } from './api';
  
  export default {
    name: 'AssessmentSummaryPage',
    components: {
      CoachAppBarPage,
      ManageExamModals,
      QuestionListPreview,
    },
    mixins: [commonCoach, coachStringsMixin, commonCoreStrings],
    data() {
      return {
        quiz: {
          active: false,
          assignments: [],
          learners_see_fixed_order: false,
          question_sources: [],
          title: '',
        },
        selectedExercises: {},
        loading: true,
        currentAction: '',
        currentView: '',
        assessmentList: [],
      };
    },
    computed: {
      ...mapState(['classList']),
      // Removing the classSummary groupMap state mapping breaks things.
      // Maybe it should live elsewhere?
      /* eslint-disable-next-line kolibri/vue-no-unused-vuex-properties */
      ...mapState('classSummary', ['groupMap', 'learnerMap']),
      selectedQuestions() {
        return this.quiz.question_sources;
      },
      quizIsRandomized() {
        return !this.quiz.learners_see_fixed_order;
      },
      avgScore() {
        return this.getExamAvgScore(this.$route.params.assessmentId, this.recipients);
      },
      exam() {
        return this.assessmentMap[this.$route.params.assessmentId];
      },
      recipients() {
        return this.getLearnersForExam(this.exam);
      },
      orderDescriptionString() {
        return this.quizIsRandomized
          ? this.coachString('orderRandomDescription')
          : this.coachString('orderFixedDescription');
      },
      classId() {
        return this.$route.params.classId;
      },

    },
    beforeRouteEnter(to, from, next) {
      AssessmentGroupDataResource.fetchModel({ id: to.params.assessmentId }).then(d => {
        this.assessmentList = Object.values(d).filter(d => typeof d !== 'string');
      })
      return fetchAssessmentSummaryPageData(to.params.assessmentId)
        .then(data => {
          next(vm => vm.setData(data));
        })
        .catch(error => {
          next(vm => vm.setError(error));
        });
    },
    mounted() {
      this.currentView = 'TEST_LISTING'
    },
    methods: {
      // @public
      toggleView(view) {
        this.currentView = view;
      },
      // @public
      setData(data) {
        const { exam, exerciseContentNodes } = data;
        this.quiz = exam;
        this.selectedExercises = fromPairs(exerciseContentNodes.map(x => [x.id, x]));
        this.loading = false;
        this.$store.dispatch('notLoading');
      },
      // @public
      setError(error) {
        this.$store.dispatch('handleApiError', { error });
        this.loading = false;
        this.$store.dispatch('notLoading');
      },
      // @public
      setCurrentAction(action) {
        if (action === 'EDIT_DETAILS') {
          this.$router.push(this.$router.getRoute('QuizEditDetailsPage'));
        } else {
          this.currentAction = action;
        }
      },
      closeModal() {
        this.currentAction = '';
      },
      handleSubmitCopy({ classroomId, groupIds, adHocLearnerIds, examTitle }) {
        const title = examTitle
          .trim()
          .substring(0, 50)
          .trim();

        const className = find(this.classList, { id: classroomId }).name;
        const assignments = serverAssignmentPayload(groupIds, classroomId);

        this.$store
          .dispatch('examReport/copyExam', {
            exam: {
              collection: classroomId,
              title,
              question_count: this.quiz.question_count,
              question_sources: this.quiz.question_sources,
              assignments,
              learner_ids: adHocLearnerIds,
              date_archived: null,
              date_activated: null,
            },
            className,
          })
          .then(result => {
            this.showSnackbarNotification('quizCopied');
            // If exam was copied to the current classroom, add it to the classSummary module
            if (classroomId === this.classId) {
              const object = {
                id: result.id,
                title: result.title,
                groups: clientAssigmentState(groupIds.concat(), this.classId),
                active: false,
              };
              this.$store.commit('classSummary/CREATE_ITEM', {
                map: 'examMap',
                id: object.id,
                object,
              });
            }
            this.closeModal();
          })
          .catch(error => {
            const caughtErrors = CatchErrors(error, [ERROR_CONSTANTS.UNIQUE]);
            if (caughtErrors) {
              this.$store.commit('CORE_CREATE_SNACKBAR', {
                text: this.$tr('uniqueTitleError', {
                  title,
                  className,
                }),
                autoDismiss: false,
                actionText: this.coreString('closeAction'),
                actionCallback: () => this.$store.commit('CORE_CLEAR_SNACKBAR'),
              });
            } else {
              this.$store.dispatch('handleApiError', { error });
            }
            this.$store.dispatch('notLoading');
            this.closeModal();
          });
      },
      handleSubmitDelete() {
        return deleteExam(this.quiz.id)
          .then(() => {
            this.$store.commit('classSummary/DELETE_ITEM', { map: 'examMap', id: this.quiz.id });
            this.$router.replace(this.$router.getRoute('EXAMS'), () => {
              this.showSnackbarNotification('quizDeleted');
            });
          })
          .catch(error => {
            this.$store.dispatch('handleApiError', { error });
          });
      },
    },
    $trs: {
      uniqueTitleError: {
        message: `A quiz titled '{title}' already exists in '{className}'`,
        context:
          'Displays if user attempts to give a quiz the same name as one that already exists.',
      },
    },
  };

</script>


<style lang="scss" scoped>

  // HACK: to prevent perseus multi-choice tiles from appearing
  // over modal overlay and snackbar
  /deep/ .perseus-radio-selected {
    z-index: 0 !important;
  }

  .back-arrow {
  color: blue;
  display: inline-flex;
  gap: 6px;
  cursor: pointer;
  & span {
    text-decoration: underline;
  }
}

.table-title {
  color: blue;
  cursor: pointer ;
  margin: 2px 0px 3px 0px;
}

</style>
