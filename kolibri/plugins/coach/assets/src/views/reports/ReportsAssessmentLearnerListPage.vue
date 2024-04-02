<template>

  <ReportsAssessmentBaseListPage :assessmentDetails="assessmentDetails" @export="exportCSV">
    <ReportsAssessmentTestsTable
      v-if="currentView === 'TEST_LIST'"
      :entries="testTable"
      @testTitleClick="onTestTitleClick"
    />
    <ReportsAssessmentBreakdownTable
      v-if="currentView === 'TEST_BREAKDOWN'"
      :entries="breakdownData"
      @backClick="onBackClick"
    />
  </ReportsAssessmentBaseListPage>
  
</template>
  
  
  <script>
  
    import sortBy from 'lodash/sortBy';
    import { AssessmentGroupDataResource } from 'kolibri.resources';
    import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
    import { PageNames } from '../../constants';
    import commonCoach from '../common';
    import CSVExporter from '../../csv/exporter';
    import * as csvFields from '../../csv/fields';
    import ReportsAssessmentBaseListPage from './ReportsAssessmentBaseListPage.vue';
    import ReportsAssessmentTestsTable from './ReportsAssessmentTestsTable.vue';
    import ReportsAssessmentBreakdownTable from './ReportsAssessmentBreakdownTable.vue';
  
    export default {
      name: 'ReportsAssessmentLearnerListPage',
      components: {
        ReportsAssessmentBaseListPage,
        ReportsAssessmentTestsTable,
        ReportsAssessmentBreakdownTable,
      },
      mixins: [commonCoach, commonCoreStrings],
      data() {
        return {
          currentView: 'TEST_LIST',
          breakdownData: [],
          assessmentDetails: {},
        };
      },
      computed: {
        exam() {
          return {}
          //  this.assessmentMap[this.$route.params.quizId];
        },
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
        table() {
          return []
          // const learners = this.recipients.map(learnerId => this.learnerMap[learnerId]);
          // const sorted = sortBy(learners, ['name']);
          // return sorted.map(learner => {
          //   const tableRow = {
          //     groups: this.getGroupNamesForLearner(learner.id),
          //     statusObj: this.getExamStatusObjForLearner(this.exam.id, learner.id),
          //     link: this.detailLink(learner.id),
          //   };
          //   Object.assign(tableRow, learner);
          //   return tableRow;
          // });
        },
      },
      created() {
        this.fetchAssessmentGroupDetails();
      },
      methods: {
        exportCSV() {
          const columns = [
            ...csvFields.name(),
            ...csvFields.learnerProgress('statusObj.status'),
            ...csvFields.score(),
            ...csvFields.quizQuestionsAnswered(this.exam),
            ...csvFields.list('groups', 'groupsLabel'),
          ];
  
          const exporter = new CSVExporter(columns, this.className);
          exporter.addNames({
            resource: this.exam.title,
          });
  
          exporter.export(this.table);
        },
        onTestTitleClick(assessmentId) {
          console.log("assessmentId", assessmentId)
          this.breakdownData = [{
            id: 1,
            title: 'Topic 1',
            question_count: 4,
          }, {
            id: 2,
            title: 'Topic 2',
            question_count: 6,
          }]
          this.currentView = 'TEST_BREAKDOWN'
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
  