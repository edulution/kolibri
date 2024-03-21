<template>

  <ReportsAssessmentBaseListPage @export="exportCSV">
    <ReportsLearnersTable :entries="table" :questionCount="exam.question_count" />
  </ReportsAssessmentBaseListPage>
  
</template>
  
  
  <script>
  
    import sortBy from 'lodash/sortBy';
    import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
    import { PageNames } from '../../constants';
    import commonCoach from '../common';
    import CSVExporter from '../../csv/exporter';
    import * as csvFields from '../../csv/fields';
    import ReportsAssessmentBaseListPage from './ReportsAssessmentBaseListPage';
    import ReportsLearnersTable from './ReportsLearnersTable';
  
    export default {
      name: 'ReportsAssessmentsLearnerListPage',
      components: {
        ReportsAssessmentBaseListPage,
        ReportsLearnersTable,
      },
      mixins: [commonCoach, commonCoreStrings],
      computed: {
        exam() {
          return this.examMap[this.$route.params.quizId];
        },
        recipients() {
          return this.getLearnersForExam(this.exam);
        },
        table() {
          const learners = this.recipients.map(learnerId => this.learnerMap[learnerId]);
          const sorted = sortBy(learners, ['name']);
          return sorted.map(learner => {
            const tableRow = {
              groups: this.getGroupNamesForLearner(learner.id),
              statusObj: this.getExamStatusObjForLearner(this.exam.id, learner.id),
              link: this.detailLink(learner.id),
            };
            Object.assign(tableRow, learner);
            return tableRow;
          });
        },
      },
      methods: {
        detailLink(learnerId) {
          return this.classRoute(PageNames.REPORTS_ASSESSMENT_LEARNER_PAGE_ROOT, {
            learnerId,
          });
        },
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
  