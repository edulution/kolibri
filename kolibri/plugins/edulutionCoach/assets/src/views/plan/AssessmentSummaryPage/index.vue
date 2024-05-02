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
          examOrLesson="assessment"
          :assessmentTitle="assessment.title"
          :assessmentCreatedDate="assessment.date_created"
        />

      </KGridItem>

      <KGridItem :layout12="{ span: 4 }">
        <h2 class="visuallyhidden">
          {{ coachString('generalInformationLabel') }}
        </h2>
        <AssessmentStatus
          :className="className"
          :groupAndAdHocLearnerNames="getRecipientNameForAssessment(assessment)"
          :exam="assessment"
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
                <th>{{ $tr('titleLabel') }}</th>
                <th>{{ $tr('scoreLabel') }}</th>
                <th 
                  :style="{
                    display: 'flex',
                    justifyContent: 'center'
                  }"
                >
                  {{ $tr('actionLabel') }}
                </th>
              </template>
              <template #tbody>
                <transition-group tag="tbody" name="list">
                  <tr v-for="tableRow of assessmentTestData" :key="tableRow.id" data-test="entry">
                    <td>
                      <KLabeledIcon
                        icon="topic"
                        :label="tableRow.title"
                      />
                    </td>
                  
                    <td>
                      <span
                        class="score-chip"
                        :style="{
                          backgroundColor: scoreColor(calcPercentage(tableRow.score, tableRow.questionCount)),
                          color: 'white',
                        }"
                      >
                        {{
                          $formatNumber(
                            calcPercentage(tableRow.score, tableRow.questionCount),
                            { style: 'percent' }
                          )
                        }}
                      </span>
                    </td>
                     
                    <td 
                      :style="{
                        display: 'flex',
                        justifyContent: 'space-between'
                      }"
                    >
                      <span 
                        class="btn-style"
                        @click.prevent="toggleView('QUESTION_PREVIEW',tableRow.id)"
                      >
                        View Details
                      </span>
                      <span 
                        class="btn-style"
                        @click.prevent="restartBtn(tableRow.id)"
                      >
                        restart
                      </span>
                      <span
                        class="btn-style"
                      >
                        stop
                      </span>
                    </td>
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
      :quiz="assessment"
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
        assessment: {
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
        selectedId:null,
        assessmentTestData:[]
      };
    },
    computed: {
      ...mapState(['classList']),
      // Removing the classSummary groupMap state mapping breaks things.
      // Maybe it should live elsewhere?
      /* eslint-disable-next-line kolibri/vue-no-unused-vuex-properties */
      ...mapState('classSummary', ['groupMap', 'learnerMap', 'assessmentMap']),
      selectedQuestions() {
        return this.assessment.question_sources;
      },
      quizIsRandomized() {
        return !this.assessment.learners_see_fixed_order;
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
      const testData = []
      for( const id of d.assessments){
         
         const totalQuestion = d.learner_status.find(i => i.assessment_id == id.id)
         const data ={
           id: id.id,
           questionCount :  id.question_sources.length,
           title : id.title,
           score: totalQuestion.correct_question_ids.length,
           hasRestart: true,
         }

         testData.push(data)
       }
      next(vm => {
        vm.assessmentList = d.assessments
        vm.assessmentTestData = testData
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
        this.assessment.question_sources = selectedQuestionSource?.question_sources
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
      calcPercentage(score, total) {
          return (score / total);
        },
      scoreColor(value) {
          if (value <= 0) {
            return '#D9D9D9';
          }
          if (value > 0 && value <= 0.25) {
            return '#FF412A';
          }
          if (value > 0.25 && value <= 0.50) {
            return '#EC9090';
          }
          if (value > 0.50 && value <= 0.69) {
            return '#F5C216';
          }
          if (value > 0.69 && value <= 0.74) {
            return '#99CC33';
          }
          if (value <= 1) {
            return '#00B050';
          }
        },
        restartBtn (id) {
           console.log(id,"id")
        },
      async fetchAssessmentGroupDetails() {
          const response = await AssessmentGroupDataResource.fetchModel({ id: this.$route.params.assessmentId })
          this.loading = false;
          this.assessment = {
            ...response,
            groups: [],
            assignments: [response.learner_id],
          };
        },

        async fetchSelectedExcercise() {
          const response = await ContentNodeResource.fetchCollection({getParams: {ids: map(this.assessment.question_sources, 'exercise_id'),}})
          this.setData(response)
        }
    },
    $trs: {
        titleLabel: {
          message: 'Test',
          context: '',
        },
        scoreLabel: {
          message: 'Score',
          context: '',
        },
        actionLabel :{
          message: 'Action',
          context: '',
        },
        restartLabel:{
          message: 'Restart',
          context: '', 
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

.score-chip {
      display: inline-flex;
      padding: 4px 8px;
      align-items: center;
      justify-content: center;
      border-radius: 50px;
      min-width: 100px;
    }

  .btn-style{
    color: blue;
    cursor: pointer;
    border-radius: 8px;
    padding: 2px 9px;
    box-shadow: 0 2px 3px 1px rgba(0, 0, 0, 0.2)
  }

</style>
