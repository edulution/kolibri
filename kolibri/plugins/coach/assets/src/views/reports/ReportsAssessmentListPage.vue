<template>

  <CoachAppBarPage
    :authorized="userIsAuthorized"
    authorizedRole="adminOrCoach"
    :showSubNav="true"
  >
  
    <KPageContainer :class="{ 'print': $isPrint }">
      <ReportsHeader
        :activeTabId="ReportsTabs.ASSESSMENT"
        :title="$isPrint ? $tr('printLabel', { className }) : null"
      />
      <KTabsPanel
        :tabsId="REPORTS_TABS_ID"
        :activeTabId="ReportsTabs.ASSESSMENT"
      >
        <ReportsControls @export="exportCSV">
          <KSelect
            v-model="filter"
            :label="coachString('filterQuizStatus')"
            :options="filterOptions"
            :inline="true"
          />
        </ReportsControls>

        <CoreTable :emptyMessage="emptyMessage">
          <template #headers>
            <th>{{ coachString('titleLabel') }}</th>
            <th>{{ coachString('recipientsLabel') }}</th>
            <th v-show="!$isPrint">
              {{ coachString('statusLabel') }}
            </th>
          </template>
          <template #tbody>
            <transition-group
              tag="tbody"
              name="list"
            >
              <tr
                v-for="tableRow in table"
                :key="tableRow.id"
              >
                <td>
                  <KRouterLink
                    :text="tableRow.title"
                    :to="classRoute('ReportsAssessmentLearnerListPage', { quizId: tableRow.id })"
                    icon="quiz"
                  />
                </td>
                <td>
                  <Recipients
                    :groupNames="getRecipientNameForAssessment(tableRow)"
                    :hasAssignments="tableRow.hasAssignments"
                  />
                </td>
                <td v-show="!$isPrint">
                  <div
                    v-if="!tableRow.active && !tableRow.archive"
                    class="quiz-closed-label"
                  >
                    {{ $tr('openAssessmentLabel') }}
                  </div>
                  <div
                    v-if="tableRow.active && !tableRow.archive"
                    class="quiz-closed-label"
                  >
                    {{ $tr('closeAssessmentLabel') }}
                  </div>
                  <div
                    v-if="tableRow.archive"
                    class="quiz-closed-label"
                  >
                    {{ coachString('assessmentClosedLabel') }}
                  </div>
                </td>
              </tr>
            </transition-group>
          </template>
        </CoreTable>
      </KTabsPanel>
    </KPageContainer>
  </CoachAppBarPage>
  
</template>
  
  
  <script>
  
    import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
    import { REPORTS_TABS_ID, ReportsTabs } from '../../constants/tabsConstants';
    import commonCoach from '../common';
    import CoachAppBarPage from '../CoachAppBarPage';
    import CSVExporter from '../../csv/exporter';
    import * as csvFields from '../../csv/fields';
    import ReportsControls from './ReportsControls';
    import ReportsHeader from './ReportsHeader';
  
    export default {
      name: 'ReportsAssessmentListPage',
      components: {
        CoachAppBarPage,
        ReportsControls,
        ReportsHeader,
      },
      mixins: [commonCoach, commonCoreStrings],
      data() {
        return {
          REPORTS_TABS_ID,
          ReportsTabs,
          filter: 'allAssessments',
        };
      },
      computed: {
        emptyMessage() {
          if (this.filter.value === 'allAssessments') {
            return this.coachString('assessmenListEmptyState');
          }
          if (this.filter.value === 'startedAssessments') {
            return this.coreString('noResultsLabel');
          }
          if (this.filter.value === 'assessmentsNotStarted') {
            return this.coreString('noResultsLabel');
          }
          if (this.filter.value === 'endedAssessments') {
            return this.$tr('noEndedAssessments');
          }
  
          return '';
        },
        filterOptions() {
          return [
            {
              label: this.coachString('filterQuizAll'),
              value: 'allAssessments',
              noStartedExams: 'No started assessments',
              noExamsNotStarted: 'No assessments not started',
            },
            {
              label: this.coachString('filterQuizStarted'),
              value: 'startedAssessments',
            },
            {
              label: this.coachString('filterQuizNotStarted'),
              value: 'assessmentsNotStarted',
            },
            {
              label: this.coachString('filterQuizEnded'),
              value: 'endedAssessments',
            },
          ];
        },
        table() {
          const filtered = this.assessmentGroups.filter(assessment => {
            if (this.filter.value === 'allAssessments') {
              return true;
            } else if (this.filter.value === 'startedAssessments') {
              return assessment.active && !assessment.archive;
            } else if (this.filter.value === 'assessmentsNotStarted') {
              return !assessment.active;
            } else if (this.filter.value === 'endedAssessments') {
              return assessment.active && assessment.archive;
            }
          });
          const sorted = this._.orderBy(filtered, ['date_created'], ['desc']);
          return sorted.map(assessment => {
            const learnersForQuiz = this.getLearnersForExam(assessment);
            const tableRow = {
              totalLearners: learnersForQuiz.length,
              tally: this.getAssessmentStatusTally(assessment.id, learnersForQuiz),
              groupNames: this.getGroupNames(assessment.groups),
              recipientNames: this.getRecipientNamesForExam(assessment),
              avgScore: this.getExamAvgScore(assessment.id, learnersForQuiz),
              hasAssignments: learnersForQuiz.length > 0,
            };
            Object.assign(tableRow, assessment);
            return tableRow;
          });
        },
      },
      beforeMount() {
        this.filter = this.filterOptions[0];
      },
      methods: {
        exportCSV() {
          const columns = [
            ...csvFields.title(),
            ...csvFields.avgScore(),
            ...csvFields.recipients(this.className),
            ...csvFields.tally(),
          ];
  
          const fileName = this.$tr('printLabel', { className: this.className });
          new CSVExporter(columns, fileName).export(this.table);
        },
      },
      $trs: {
        noEndedAssessments: {
          message: 'No ended assessments',
          context:
            'Message displayed when there are no ended quizes. Ended assessments are those that are no longer in progress.',
        },
        printLabel: {
          message: '{className} Assessments',
          context:
            "Title that displays on a printed copy of the 'Reports' > 'Assessments' page. This shows if the user uses the 'Print' option by clicking on the printer icon and displays on the downloadable CSV file.",
        },
        openAssessmentLabel: {
          message: 'Assessment not started',
          context: '',
        },
        closeAssessmentLabel: {
          message: 'Assessment started',
          context: '',
        }
      },
    };
  
  </script>
  
  
  <style lang="scss" scoped>
  
    @import '../common/print-table';
  
    .center-text {
      text-align: center;
    }
  
    .button-col {
      vertical-align: middle;
    }
  
  </style>
  