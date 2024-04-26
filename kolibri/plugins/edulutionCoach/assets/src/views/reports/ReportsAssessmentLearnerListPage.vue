<template>

  <ReportsAssessmentBaseListPage :assessmentDetails="assessmentDetails" @export="exportCSV">
    <ReportsAssessmentTestsTable
      v-if="currentView === 'TEST_LIST'"
      :entries="testTable"
      @testTitleClick="onTestTitleClick"
      @viewDetailClick="onViewDetailClick"
      @viewAttemptsClick="onviewAttemptsClick"
    />
    <ReportsAssessmentBreakdownTable
      v-if="currentView === 'TEST_BREAKDOWN'"
      :entries="breakdownData"
      @backClick="onBackClick"
    />
    <ReportsAssessmentDetailTable
      v-if="currentView === 'TEST_DETAIL'"
      :entries="breakdownData"
      @backClick="onBackClick"
    />
    <ReportsAssessmentAttemptsTable
      v-if="currentView === 'TEST_ATTEMPTS'"
      :entries="breakdownData"
      @backClick="onBackClick"
    />
  </ReportsAssessmentBaseListPage>
  
</template>
  
  
  <script>
  
    import { AssessmentGroupDataResource } from 'kolibri.resources';
    import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
    import commonCoach from '../common';
    import CSVExporter from '../../csv/exporter';
    import * as csvFields from '../../csv/fields';
    import ReportsAssessmentBaseListPage from './ReportsAssessmentBaseListPage.vue';
    import ReportsAssessmentTestsTable from './ReportsAssessmentTestsTable.vue';
    import ReportsAssessmentBreakdownTable from './ReportsAssessmentBreakdownTable.vue';
    import ReportsAssessmentDetailTable from './ReportsAssessmentDetailTable.vue';
    import ReportsAssessmentAttemptsTable from './ReportsAssessmentAttemptsTable.vue'

    export default {
      name: 'ReportsAssessmentLearnerListPage',
      components: {
        ReportsAssessmentBaseListPage,
        ReportsAssessmentTestsTable,
        ReportsAssessmentBreakdownTable,
        ReportsAssessmentDetailTable,
        ReportsAssessmentAttemptsTable
      },
      mixins: [commonCoach, commonCoreStrings],
      data() {
        return {
          currentView: 'TEST_LIST',
          breakdownData: [],
          assessmentDetails: {},
          selectedTest: '',
        };
      },
      computed: {
        testTable() {
          if (this.assessmentDetails.assessments) {
            return this.assessmentDetails.assessments.map(d => {
              const statusData = this.assessmentDetails.learner_status.find(l => l.assessment_id === d.id)
              return {
                id: d.id,
                title: d.title,
                question_count: d.question_sources.length,
                score: statusData?.correct_question_ids?.length || null,
              }
            })
          }
          return []
        },
      },
      created() {
        this.fetchAssessmentGroupDetails();
      },
      methods: {
        exportCSV() {

          if(this.currentView === 'TEST_LIST'){
              const columns = [
              ...csvFields.assessmentName(),
              ...csvFields.assessmentScore(),
            ];
              const exporter = new CSVExporter(columns, this.className);
              exporter.addNames({
              resource: this.assessmentDetails.title,
          });
            exporter.export(this.testTable);

          }else if(this.currentView === 'TEST_BREAKDOWN'){
            const columns = [
            ...csvFields.assessmentName(),
            ...csvFields.assessmentScore('breakdown'),
          ];
          const exporter = new CSVExporter(columns, this.className);
            exporter.addNames({
            resource: this.selectedTest,
          });
            exporter.export(this.breakdownData);
          }
  
        },
        onTestTitleClick(assessmentId) {
          if (this.assessmentDetails.assessments) {
              const statusData = this.assessmentDetails?.learner_status?.find(l => l.assessment_id === assessmentId)

              const selectedAssessments = this.assessmentDetails?.assessments.find(i => i.id === assessmentId)
              const selectedExcerciseId = selectedAssessments.exercises.map(i => i.id)

              const selectedTest = this.assessmentDetails?.assessments.find(i => i.id === assessmentId)

              this.selectedTest = selectedTest.title

              selectedExcerciseId.forEach(element =>{ 
              const selectedQuestion =  selectedAssessments?.question_sources?.filter(i => i.exercise_id === element)
              const topicTitle = [...new Set(selectedQuestion.map(i => i.title))]
              const topicId = selectedQuestion.map(i => i.exercise_id)

              const selectedCorrectQuestion = [] 

              for(const correctQuesitons of  selectedQuestion){
               if (statusData?.correct_question_ids.includes(correctQuesitons.question_id)){
                  selectedCorrectQuestion.push(correctQuesitons.question_id)
               }
              }
         
              const breakdownData = {
                      id: topicId,
                      title: topicTitle.join(''),
                      question_count: selectedQuestion?.length,
                      score: selectedCorrectQuestion.length || null,
                    }
              this.breakdownData.push(breakdownData);      
            });        
          }
          this.currentView = 'TEST_BREAKDOWN'
        },
        onViewDetailClick(assessmentId){
          if (this.assessmentDetails.assessments) {
            console.log(assessmentId,"assessmentId")       
          }
          this.currentView = 'TEST_DETAIL'
        },
        onviewAttemptsClick(assessmentId) {
          if (this.assessmentDetails.assessments) {
              console.log(assessmentId,"assessmentId")      
          }
          this.currentView = 'TEST_ATTEMPTS'
        },
        onBackClick() {
          this.breakdownData = []
          this.currentView = 'TEST_LIST'
        },
        async fetchAssessmentGroupDetails() {
          const response = await AssessmentGroupDataResource.fetchModel({ id: this.$route.params.quizId })
          this.assessmentDetails = {
            ...response,
            groups: [],
            assignments: [response.learner_id],
          };
        }
      },
    };
  
  </script>
  
  
  <style lang="scss" scoped>
  
    @import '../common/print-table';
  
    .small-answered-count {
      display: block;
      margin-left: 1.75rem; /* matches KLabeledIcon */
      font-size: small;
    }
  
  </style>
  