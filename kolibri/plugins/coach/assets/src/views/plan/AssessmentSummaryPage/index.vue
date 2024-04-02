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
          :groupAndAdHocLearnerNames="getRecipientNameForAssessment(quiz)"
          :exam="quiz"
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
                      :label="tableRow.title" 
                      class="table-title"
                      @click.prevent="toggleView('QUESTION_PREVIEW',tableRow.id)"
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
  import { AssessmentGroupDataResource ,ContentNodeResource } from 'kolibri.resources';
  import { mapState } from 'vuex';
  import fromPairs from 'lodash/fromPairs';
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import map from 'lodash/map';
  import commonCoach from '../../common';
  import CoachAppBarPage from '../../CoachAppBarPage';
  import QuestionListPreview from '../CreateExamPage/QuestionListPreview';
  import { coachStringsMixin } from '../../common/commonCoachStrings';
  import ManageExamModals from './ManageExamModals';
  
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
        selectedId:null 
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
      orderDescriptionString() {
        return this.quizIsRandomized
          ? this.coachString('orderRandomDescription')
          : this.coachString('orderFixedDescription');
      },

    },
    beforeRouteEnter(to, from, next) {
  const fetchData = async () => {
    try {
      const d = await AssessmentGroupDataResource.fetchModel({ id: to.params.assessmentId });
      next(vm => {
        vm.assessmentList = d.assessments;
      });
    } catch (error) {
      // Handle error
      console.error(error);
    }
  };
  fetchData();
},
    mounted() {
      this.currentView = 'TEST_LISTING'
    },
    created() {
        this.fetchAssessmentGroupDetails();
        this.fetchSelectedExcercise()
      },
    methods: {
      // @public
      toggleView(view,id) {
        this.currentView = view;
        this.selectedId = id
        const selectedQuestionSource = this.assessmentList.find(d => d.id == this.selectedId)
        this.quiz.question_sources = selectedQuestionSource?.question_sources
      },
      // @public
      setData(data) {
        this.selectedExercises = fromPairs(data.map(x => [x.id, x]));
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
      async fetchAssessmentGroupDetails() {
          const response = await AssessmentGroupDataResource.fetchModel({ id: this.$route.params.assessmentId })
          this.loading = false;
          this.quiz = {
            ...response,
            groups: [],
            assignments: [response.learner_id],
          };
        },

        async fetchSelectedExcercise() {
          const response = await ContentNodeResource.fetchCollection({getParams: {ids: map(this.quiz.question_sources, 'exercise_id'),}})
          this.setData(response)
        }
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
  color: #071D49;
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
