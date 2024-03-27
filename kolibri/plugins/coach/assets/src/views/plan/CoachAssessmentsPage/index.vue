<template>

  <CoachAppBarPage
    :authorized="userIsAuthorized"
    authorizedRole="adminOrCoach"
    :showSubNav="true"
  >

    <KPageContainer>
      <PlanHeader :activeTabId="PlanTabs.ASSESSMENT" />
      <KTabsPanel
        :tabsId="PLAN_TABS_ID"
        :activeTabId="PlanTabs.ASSESSMENT"
      >
        <div class="filter-and-button">
          <p v-if="filteredExams.length && filteredExams.length > 0">
            {{ $tr('totalAssessmentSize', { size: calcTotalSizeOfVisibleQuizzes }) }}
          </p>
          <KSelect
            v-model="statusSelected"
            :label="coachString('filterQuizStatus')"
            :options="statusOptions"
            :inline="true"
          />
          <KButtonGroup v-if="practiceQuizzesExist">
            <KButton
              primary
              hasDropdown
              appearance="raised-button"
              :text="coachString('newAssessmentAction')"
            >
              <template #menu>
                <KDropdownMenu
                  :options="dropdownOptions"
                  class="options-btn"
                  @select="handleSelect"
                />
              </template>
            </KButton>
          </KButtonGroup>
          <div
            v-else
            class="button"
          >
            <KRouterLink
              :primary="true"
              appearance="raised-button"
              :to="newExamRoute"
              :text="coachString('newAssessmentAction')"
            />
          </div>
        </div>
        <CoreTable :emptyMessage="emptyMessage">
          <template #headers>
            <th>{{ coachString('titleLabel') }}</th>
            <th>{{ coachString('recipientsLabel') }}</th>
            <th>{{ coachString('sizeLabel') }}</th>
            <th class="center-text">
              {{ coachString('statusLabel') }}
            </th>
          </template>
          <template #tbody>
            <transition-group
              tag="tbody"
              name="list"
            >
              <tr
                v-for="exam in filteredExams"
                :key="exam.id"
              >
                <td>
                  <KRouterLink
                    :to="$router.getRoute(PageNames.ASSESSMENT_QUIZ_SUMMARY, { quizId: exam.id })"
                    appearance="basic-link"
                    :text="exam.title"
                    icon="quiz"
                  />
                </td>

                <td>
                  <Recipients
                    :groupNames="getRecipientNamesForExam(exam)"
                    :hasAssignments="exam.assignments.length > 0"
                  />
                </td>
                <td>
                  {{ exam.size_string ? exam.size_string : '--' }}
                </td>
                <td class="button-col center-text core-table-button-col">
                  <!-- Open quiz button -->
                  <KButton
                    v-if="!exam.active && !exam.archive"
                    :text="coachString('openAssessmentLabel')"
                    appearance="flat-button"
                    @click="showOpenConfirmationModal = true; activeQuiz = exam"
                  />
                  <!-- Close quiz button -->
                  <KButton
                    v-if="exam.active && !exam.archive"
                    :text="coachString('closeAssessmentLabel')"
                    appearance="flat-button"
                    @click="showCloseConfirmationModal = true; activeQuiz = exam;"
                  />
                  <!-- Closed quiz label -->
                  <div v-if="exam.archive">
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
          @submit="handleOpenQuiz(activeQuiz.id)"
        >
          <p>{{ coachString('openAssessmentModalDetail') }}</p>
          <p>{{ coachString('lodAssessmentDetail') }}</p>
          <p>{{ coachString('fileSizeToDownload', { size: activeQuiz.size_string }) }}</p>
        </KModal>
        <KModal
          v-if="showCloseConfirmationModal"
          :title="coachString('closeAssessmentLabel')"
          :submitText="coreString('continueAction')"
          :cancelText="coreString('cancelAction')"
          @cancel="showCloseConfirmationModal = false"
          @submit="handleCloseQuiz(activeQuiz.id)"
        >
          <div>{{ coachString('closeAssessmentModalDetail') }}</div>
        </KModal>
      </KTabsPanel>
    </KPageContainer>
  </CoachAppBarPage>

</template>


<script>

  import CoreTable from 'kolibri.coreVue.components.CoreTable';
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import { AssessmentResource } from 'kolibri.resources';
  import plugin_data from 'plugin_data';
  import bytesForHumans from 'kolibri.utils.bytesForHumans';
  import { mapActions } from 'vuex';
  import { PageNames } from '../../../constants';
  import { PLAN_TABS_ID, PlanTabs } from '../../../constants/tabsConstants';
  import commonCoach from '../../common';
  import CoachAppBarPage from '../../CoachAppBarPage';
  import PlanHeader from '../../plan/PlanHeader';

  export default {
    name: 'CoachAssessmentsPage',
    components: {
      CoreTable,
      CoachAppBarPage,
      PlanHeader,
    },
    mixins: [commonCoach, commonCoreStrings],
    data() {
      return {
        PLAN_TABS_ID,
        PlanTabs,
        statusSelected: {
          label: this.coachString('filterQuizAll'),
          value: this.coachString('filterQuizAll'),
        },
        showOpenConfirmationModal: false,
        showCloseConfirmationModal: false,
        activeQuiz: null,
        learnOnlyDevicesExist: false,
      };
    },
    computed: {
      sortedExams() {
        return this._.orderBy(this.assessments, ['date_created'], ['desc']);
      },
      practiceQuizzesExist() {
        return plugin_data.practice_quizzes_exist;
      },
      statusOptions() {
        return [
          {
            label: this.coachString('filterQuizAll'),
            value: this.coachString('filterQuizAll'),
          },
          {
            label: this.coachString('filterQuizStarted'),
            value: this.coachString('filterQuizStarted'),
          },
          {
            label: this.coachString('filterQuizNotStarted'),
            value: this.coachString('filterQuizNotStarted'),
          },
          {
            label: this.coachString('filterQuizEnded'),
            value: this.coachString('filterQuizEnded'),
          },
        ];
      },
      startedExams() {
        return this.sortedExams.filter(
          assessment => assessment.active === true && assessment.archive === false);
      },
      endedExams() {
        return this.sortedExams.filter(
          assessment => assessment.active === true && assessment.archive === true);
      },
      notStartedExams() {
        return this.sortedExams.filter(assessment => assessment.active === false);
      },
      filteredExams() {
        const filter = this.statusSelected.label;
        if (filter === this.coachString('filterQuizStarted')) {
          return this.startedExams;
        } else if (filter === this.coachString('filterQuizNotStarted')) {
          return this.notStartedExams;
        } else if (filter === this.coachString('filterQuizEnded')) {
          return this.endedExams;
        }
        return this.sortedExams;
      },
      emptyMessage() {
        if (this.statusSelected.value === this.coachString('filterQuizAll')) {
          return this.coachString('assessmenListEmptyState');
        }
        if (this.statusSelected.value === this.coachString('filterQuizStarted')) {
          return this.coreString('noResultsLabel');
        }
        if (this.statusSelected.value === this.coachString('filterQuizNotStarted')) {
          return this.coreString('noResultsLabel');
        }
        if (this.statusSelected.value === this.coachString('filterQuizEnded')) {
          return this.$tr('noEndedAssessments');
        }

        return '';
      },
      newExamRoute() {
        return { name: PageNames.ASSESSMENT_CREATION_ROOT };
      },
      dropdownOptions() {
        return [
          { label: this.$tr('newAssessment'), value: 'MAKE_NEW_QUIZ' },
          { label: this.$tr('selectAssessment'), value: 'SELECT_QUIZ' },
        ];
      },
      calcTotalSizeOfVisibleQuizzes() {
        if (this.filteredExams) {
          let sum = 0;
          this.filteredExams.forEach(exam => {
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
    mounted() {
      this.checkIfAnyLODsInClass();
    },
    methods: {
      ...mapActions(['fetchUserSyncStatus']),
      // modal about lesson sizes should only exist of LODs exist in the class
      // which we are checking via if there have recently been any user syncs
      // TODO: refactor to a more robust check
      checkIfAnyLODsInClass() {
        this.fetchUserSyncStatus({ member_of: this.$route.params.classId }).then(data => {
          if (data && data.length > 0) {
            this.learnOnlyDevicesExist = true;
          }
        });
      },
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
      handleSelect({ value }) {
        const nextRoute = {
          MAKE_NEW_QUIZ: PageNames.EXAM_CREATION_ROOT,
          SELECT_QUIZ: PageNames.EXAM_CREATION_PRACTICE_QUIZ,
        }[value];
        this.$router.push(this.$router.getRoute(nextRoute));
      },
    },
    $trs: {
      newAssessment: {
        message: 'Create new assessment',
        context: "Title of the screen launched from the 'New quiz' button on the 'Plan' tab.\n",
      },
      selectAssessment: {
        message: 'Select assessment',
        context:
          "Practice assessments are pre-made assessments, that don't require the curation work on the part of the coach. Selecting a practice quiz refers to importing a ready-to-use quiz.",
      },
      totalAssessmentSize: {
        message: 'Total size of assessments visible to learners: {size}',
        context:
          'Descriptive text at the top of the table that displays the calculated file size of all quiz resources (i.e. 120 MB)',
      },
      noEndedAssessments: {
          message: 'No ended assessments',
          context:
            'Message displayed when there are no ended quizes. Ended assessments are those that are no longer in progress.',
        },
    },
  };

</script>


<style lang="scss" scoped>

  .filter-and-button {
    display: flex;
    flex-wrap: wrap-reverse;
    justify-content: space-between;

    button {
      align-self: flex-end;
    }
  }

  .center-text {
    text-align: center;
  }

  .button-col {
    vertical-align: middle;
  }

</style>
