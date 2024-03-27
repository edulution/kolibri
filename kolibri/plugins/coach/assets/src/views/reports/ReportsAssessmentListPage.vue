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
          <p v-if="table.length && table.length > 0">
            {{ $tr('totalQuizSize', { size: calcTotalSizeOfVisibleQuizzes }) }}
          </p>
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
            <th style="position:relative;">
              {{ coachString('avgScoreLabel') }}
              <AverageScoreTooltip v-show="!$isPrint" />
            </th>
            <th>{{ coachString('recipientsLabel') }}</th>
            <th>{{ coachString('sizeLabel') }}</th>
            <th
              v-show="!$isPrint"
              class="center-text"
            >
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
                <td  
                  :style="{ backgroundColor: 
                    scoreBackgroundColor((tableRow.avgScore) || 0) }" 
                >
                  <Score :value="tableRow.avgScore" />
                </td>
                <td>
                  <Recipients
                    :groupNames="getRecipientNamesForExam(tableRow)"
                    :hasAssignments="tableRow.hasAssignments"
                  />
                </td>
                <td>
                  {{ tableRow.size_string ? tableRow.size_string : '--' }}
                </td>
                <td
                  v-show="!$isPrint"
                  class="button-col center-text core-table-button-col"
                >
                  <!-- Open quiz button -->
                  <KButton
                    v-if="!tableRow.active && !tableRow.archive"
                    :text="coachString('openAssessmentLabel')"
                    appearance="flat-button"
                    class="table-left-aligned-button"
                    @click="showOpenConfirmationModal = true; modalQuizId = tableRow.id"
                  />
                  <!-- Close quiz button -->
                  <KButton
                    v-if="tableRow.active && !tableRow.archive"
                    :text="coachString('closeAssessmentLabel')"
                    appearance="flat-button"
                    class="table-left-aligned-button"
                    @click="showCloseConfirmationModal = true; modalQuizId = tableRow.id;"
                  />
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
        <!-- Modals for Close & Open of quiz from right-most column -->
        <KModal
          v-if="showOpenConfirmationModal"
          :title="coachString('openAssessmentLabel')"
          :submitText="coreString('continueAction')"
          :cancelText="coreString('cancelAction')"
          @cancel="showOpenConfirmationModal = false"
          @submit="handleOpenQuiz(modalQuizId)"
        >
          <p>{{ coachString('openAssessmentModalDetail') }}</p>
          <p>{{ coachString('lodAssessmentDetail') }}</p>
          <p>{{ coachString('fileSizeToDownload', { size: modalQuizId.size_string }) }}</p>
        </KModal>
        <KModal
          v-if="showCloseConfirmationModal"
          :title="coachString('closeAssessmentLabel')"
          :submitText="coreString('continueAction')"
          :cancelText="coreString('cancelAction')"
          @cancel="showCloseConfirmationModal = false"
          @submit="handleCloseQuiz(modalQuizId)"
        >
          <div>{{ coachString('closeAssessmentModalDetail') }}</div>
        </KModal>
      </KTabsPanel>
    </KPageContainer>
  </CoachAppBarPage>
  
</template>
  
  
  <script>
  
    import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
    import { AssessmentResource } from 'kolibri.resources';
    import bytesForHumans from 'kolibri.utils.bytesForHumans';
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
          showOpenConfirmationModal: false,
          showCloseConfirmationModal: false,
          modalQuizId: null,
        };
      },
      computed: {
        emptyMessage() {
          if (this.filter.value === 'allAssessments') {
            return this.coachString('quizListEmptyState');
          }
          if (this.filter.value === 'startedAssessments') {
            return this.coreString('noResultsLabel');
          }
          if (this.filter.value === 'assessmentsNotStarted') {
            return this.coreString('noResultsLabel');
          }
          if (this.filter.value === 'endedAssessments') {
            return this.$tr('noEndedExams');
          }
  
          return '';
        },
        filterOptions() {
          return [
            {
              label: this.coachString('filterQuizAll'),
              value: 'allAssessments',
              noStartedExams: 'No started quizzes',
              noExamsNotStarted: 'No quizzes not started',
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
          const filtered = this.assessments.filter(assessment => {
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
              tally: this.getExamStatusTally(assessment.id, learnersForQuiz),
              groupNames: this.getGroupNames(assessment.groups),
              recipientNames: this.getRecipientNamesForExam(assessment),
              avgScore: this.getExamAvgScore(assessment.id, learnersForQuiz),
              hasAssignments: learnersForQuiz.length > 0,
            };
            Object.assign(tableRow, assessment);
            return tableRow;
          });
        },
        calcTotalSizeOfVisibleQuizzes() {
          if (this.exams) {
            let sum = 0;
            this.exams.forEach(exam => {
              if (exam.active) {
                sum += exam.size;
              }
            });
            const size = bytesForHumans(sum);
            return size;
          }
          return '--';
        },
      },
      beforeMount() {
        this.filter = this.filterOptions[0];
      },
      methods: {
        handleOpenQuiz(quizId) {
          const promise = AssessmentResource.saveModel({
            id: quizId,
            data: {
              active: true,
              date_activated: new Date(),
            },
            exists: true,
          });
  
          return promise
            .then(() => {
              this.$store.dispatch('classSummary/refreshClassSummary');
              this.showOpenConfirmationModal = false;
              this.$store.dispatch('createSnackbar', this.coachString('assessmentOpenedMessage'));
            })
            .catch(() => {
              this.$store.dispatch('createSnackbar', this.coachString('assessmentFailedToOpenMessage'));
            });
        },
        handleCloseQuiz(quizId) {
          const promise = AssessmentResource.saveModel({
            id: quizId,
            data: {
              archive: true,
              date_archived: new Date(),
            },
            exists: true,
          });
  
          return promise
            .then(() => {
              this.$store.dispatch('classSummary/refreshClassSummary');
              this.showCloseConfirmationModal = false;
              this.$store.dispatch('createSnackbar', this.coachString('assessmentClosedMessage'));
            })
            .catch(() => {
              this.$store.dispatch('createSnackbar', this.coachString('assessmentFailedToCloseMessage'));
            });
        },
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
        scoreBackgroundColor(value) {
          if (value >= 0 && value < 30) {
            return 'red';
          } else if (value >= 30 && value < 50) {
            return 'blue';
          } else if (value >= 50 && value < 70) {
            return 'black';
          } else if (value >= 70 && value <= 100) {
            return 'pink';
          }
      },
      },
      $trs: {
        noEndedExams: {
          message: 'No ended assessments',
          context:
            'Message displayed when there are no ended quizes. Ended assessments are those that are no longer in progress.',
        },
        printLabel: {
          message: '{className} Assessments',
          context:
            "Title that displays on a printed copy of the 'Reports' > 'Assessments' page. This shows if the user uses the 'Print' option by clicking on the printer icon and displays on the downloadable CSV file.",
        },
        totalQuizSize: {
          message: 'Total size of assessments visible to learners: {size}',
          context:
            'Descriptive text at the top of the table that displays the calculated file size of all assessment resources (i.e. 120 MB)',
        },
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
  