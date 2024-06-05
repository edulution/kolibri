<template>

  <KPageContainer :topMargin="$isPrint ? 0 : 16">
    <KGrid gutter="16">
      <!-- Quiz Open button -->
      <div v-if="!exam.active && !exam.archive && !$isPrint" class="status-item">
        <KGridItem
          class="status-label"
          :layout4="{ span: 4 }"
          :layout8="{ span: 8 }"
          :layout12="{ span: 12 }"
        >
          <KButton
            v-if="isPlan"
            :primary="true"
            :text="coachString('openAssessmentLabel')"
            type="button"
            @click="showConfirmationModal = true"
          />

          <div v-if="isReport">
            {{ $tr('openAssessmentLabel') }}
          </div>
        </KGridItem>
        <KGridItem
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="{ span: 12 }"
        >
          <ElapsedTime :date="examDateCreated" />
        </KGridItem>
      </div>

      <!-- Quiz Close button & time since opened -->
      <div v-if="exam.active && !exam.archive && !$isPrint" class="status-item">
        <KGridItem
          class="status-label"
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="{ span: 12 }"
        >
          <KButton
            v-if="isPlan"
            :text="coachString('closeAssessmentLabel')"
            type="submit"
            :appearanceOverrides="cancelStyleOverrides"
            @click="showCancellationModal = true"
          />

          <div v-if="isReport">
            {{ $tr('closeAssessmentLabel') }}
          </div>
        </KGridItem>
        <KGridItem
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="{ span: 12 }"
        >
          <ElapsedTime :date="examDateOpened" />
        </KGridItem>
      </div>

      <!-- Assessment Closed label & time since closed -->
      <div v-if="exam.archive && !$isPrint" class="status-item">
        <KGridItem
          class="status-label"
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="{ span: 12 }"
        >
          {{ coachString('assessmentClosedLabel') }}
        </KGridItem>
        <KGridItem
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="{ span: 12 }"
        >
          <ElapsedTime :date="examDateArchived" />
        </KGridItem>
      </div>

      <div v-if="showReportVisible && exam.archive && !$isPrint" class="status-item">
        <KGridItem
          class="status-label"
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="{ span: 12 }"
        >
          {{ $tr('reportVisibleToLearnersLabel') }}
        </KGridItem>
        <KGridItem
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="{ span: 12 }"
        >
          <KSwitch
            name="toggle-quiz-visibility"
            label=""
            style="display:inline;"
            :checked="exam.active"
            :value="exam.active"
            @change="handleToggleVisibility"
          />
        </KGridItem>
      </div>

      <!-- Class name  -->
      <div v-show="$isPrint" class="status-item">
        <KGridItem
          class="status-label"
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="layout12Label"
        >
          {{ coachString('classLabel') }}
        </KGridItem>
        <KGridItem
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="layout12Value"
        >
          <div>
            {{ className }}
          </div>
        </KGridItem>
      </div>

      <!-- Recipients  -->
      <div class="status-item">
        <KGridItem
          class="status-label"
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="layout12Label"
        >
          {{ $tr('recipientsLabel') }}
        </KGridItem>
        <KGridItem
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="layout12Value"
        >
          <div>
            <Recipients
              :groupNames="groupAndAdHocLearnerNames"
              :hasAssignments="exam.assignments.length > 0"
            />
          </div>
        </KGridItem>
      </div>

      <!-- Average Score -->
      <!-- <div class="status-item">
        <KGridItem
          class="status-label"
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="layout12Label"
        >
          <span>{{ coachString('avgScoreLabel') }}</span>
          <AverageScoreTooltip v-show="!$isPrint" class="avg-score-info" />
        </KGridItem>
        <KGridItem
          :layout4="{ span: 4 }"
          :layout8="{ span: 4 }"
          :layout12="layout12Value"
        >
          <Score :value="avgScore" />
        </KGridItem>
      </div> -->

    </KGrid>

    <KModal
      v-if="showConfirmationModal"
      :title="coachString('openAssessmentLabel')"
      :submitText="coreString('continueAction')"
      :cancelText="coreString('cancelAction')"
      @cancel="showConfirmationModal = false"
      @submit="handleOpenQuiz"
    >
      <p>{{ coachString('openAssessmentModalDetail') }}</p>
      <p>{{ coachString('lodQuizDetail') }}</p>
      <p>{{ coachString('fileSizeToDownload', { size: exam.size_string }) }}</p>
    </KModal>

    <KModal
      v-if="showCancellationModal"
      :title="coachString('closeAssessmentLabel')"
      :submitText="coreString('continueAction')"
      :cancelText="coreString('cancelAction')"
      @cancel="showCancellationModal = false"
      @submit="handleCloseQuiz"
    >
      <div>{{ coachString('closeAssessmentModalDetail') }}</div>
    </KModal>

    <KModal
      v-if="showRemoveReportVisibilityModal"
      :title="coachString('makeAssessmentReportNotVisibleTitle')"
      :submitText="coreString('continueAction')"
      :cancelText="coreString('cancelAction')"
      @cancel="showRemoveReportVisibilityModal = false"
      @submit="makeQuizInactive(exam)"
    >
      <p>{{ coachString('makeAssessmentReportNotVisibleText') }}</p>
      <p>{{ coachString('fileSizeToRemove', { size: exam.size_string }) }}</p>
      <KCheckbox
        :checked="dontShowAgainChecked"
        :label="coachString('dontShowAgain')"
        @change="dontShowAgainChecked = $event"
      />
    </KModal>
    <KModal
      v-if="showMakeReportVisibleModal"
      :title="coachString('makeAssessmentReportVisibleTitle')"
      :submitText="coreString('continueAction')"
      :cancelText="coreString('cancelAction')"
      @cancel="showMakeReportVisibleModal = false"
      @submit="makeQuizInactive(exam)"
    >
      <p>{{ coachString('makeAssessmentReportVisibleText') }}</p>
      <p>{{ coachString('fileSizeToDownload', { size: exam.size_string }) }}</p>
      <KCheckbox
        :checked="dontShowAgainChecked"
        :label="coachString('dontShowAgain')"
        @change="dontShowAgainChecked = $event"
      />
    </KModal>

  </KPageContainer>

</template>


<script>

  import { ExamResource,AssessmentStartResource, AssessmentStopResource } from 'kolibri.resources';
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import ElapsedTime from 'kolibri.coreVue.components.ElapsedTime';
  import Lockr from 'lockr';
  import { QUIZ_REPORT_VISIBILITY_MODAL_DISMISSED } from 'kolibri.coreVue.vuex.constants';
  import { mapActions } from 'vuex';
  import { coachStringsMixin } from './commonCoachStrings';
  import Score from './Score';
  import Recipients from './Recipients';
  import AverageScoreTooltip from './AverageScoreTooltip';


  export default {
    name: 'AssessmentStatus',
    components: { Score, Recipients, ElapsedTime, AverageScoreTooltip },
    mixins: [coachStringsMixin, commonCoreStrings],
    props: {
      className: {
        type: String,
        required: true,
      },
      groupAndAdHocLearnerNames: {
        type: Array,
        required: true,
      },
      exam: {
        type: Object,
        required: true,
      },
      avgScore: {
        type: Number,
        default: null,
      },
      variant: {
        type: String,
        default: 'PLAN',
      }
    },
    data() {
      return {
        showConfirmationModal: false,
        showCancellationModal: false,
        showRemoveReportVisibilityModal: false,
        showMakeReportVisibleModal: false,
        dontShowAgainChecked: false,
        learnOnlyDevicesExist: false,
      };
    },
    computed: {
      isPlan() {
        return this.variant === 'PLAN'
      },
      isReport() {
        return this.variant === 'REPORT'
      },
      cancelStyleOverrides() {
        return {
          color: this.$themeTokens.textInverted,
          'background-color': this.$themePalette.red.v_700,
          ':hover': { 'background-color': this.$themePalette.red.v_900 },
        };
      },
      examDateCreated() {
        if (this.exam.date_created) {
          return new Date(this.exam.date_created);
        } else {
          return null;
        }
      },
      examDateArchived() {
        if (this.exam.date_archived) {
          return new Date(this.exam.date_archived);
        } else {
          return null;
        }
      },
      examDateOpened() {
        if (this.exam.date_activated) {
          return new Date(this.exam.date_activated);
        } else {
          return null;
        }
      },
      layout12Label() {
        return { span: this.$isPrint ? 3 : 12 };
      },
      layout12Value() {
        return { span: this.$isPrint ? 9 : 12 };
      },
    },
    mounted() {
      this.checkIfAnyLODsInClass();
    },
    methods: {
      ...mapActions(['fetchUserSyncStatus']),
      handleOpenQuiz() {
        const promise = AssessmentStartResource.saveModel({
          id: this.$route.params.assessmentId,
          data: {
            active: true,
            date_activated: new Date(),
          },
          exists: true,
        });

        return promise
          .then(() => {
            this.$store.dispatch('classSummary/refreshClassSummary');
            this.showConfirmationModal = false;
            this.$store.dispatch('createSnackbar', this.coachString('assessmentOpenedMessage'));
            this.$router.go(this.$router.currentRoute)
          })
          .catch(() => {
            this.$store.dispatch('createSnackbar', this.coachString('assessmentFailedToOpenMessage'));
          });
      },
      handleCloseQuiz() {
        const promise = AssessmentStopResource.saveModel({
          id: this.$route.params.assessmentId,
          data: {
            archive: true,
            date_archived: new Date(),
          },
          exists: true,
        });

        return promise
          .then(() => {
            this.$store.dispatch('classSummary/refreshClassSummary');
            this.showCancellationModal = false;
            this.$store.dispatch('createSnackbar', this.coachString('assessmentClosedMessage'));
            this.$router.go(this.$router.currentRoute)
          })
          .catch(() => {
            this.$store.dispatch('createSnackbar', this.coachString('assessmentFailedToCloseMessage'));
          });
      },
      // modal about quiz report size should only exist of LODs exist in the class
      // which we are checking via if there have recently been any user syncs
      // TODO: refactor to a more robust check
      checkIfAnyLODsInClass() {
        this.fetchUserSyncStatus({ member_of: this.$route.params.classId }).then(data => {
          if (data && data.length > 0) {
            this.learnOnlyDevicesExist = true;
          }
        });
      },
      handleToggleVisibility() {
        // has the user set their preferences to not have a modal confirmation?
        const hideModalConfirmation = Lockr.get(QUIZ_REPORT_VISIBILITY_MODAL_DISMISSED);
        if (!hideModalConfirmation && this.learnOnlyDevicesExist) {
          if (this.exam.active) {
            this.showRemoveReportVisibilityModal = true;
            this.showMakeReportVisibleModal = false;
          } else {
            this.showMakeReportVisibleModal = true;
            this.showRemoveReportVisibilityModal = false;
          }
        } else {
          // proceed with visibility changes withhout the modal
          this.makeQuizInactive(this.exam);
        }
      },
      makeQuizInactive() {
        if (this.dontShowAgainChecked) {
          Lockr.set(QUIZ_REPORT_VISIBILITY_MODAL_DISMISSED, true);
        }
        const newActiveState = !this.exam.active;
        const snackbarMessage = newActiveState
          ? this.coachString('assessmentVisibleToLearners')
          : this.coachString('assessmentNotVisibleToLearners');

        const promise = ExamResource.saveModel({
          id: this.$route.params.quizId,
          data: {
            active: newActiveState,
          },
          exists: true,
        });

        return promise.then(() => {
          this.$store.dispatch('classSummary/refreshClassSummary');
          this.showConfirmationModal = false;
          this.showRemoveReportVisibilityModal = false;
          this.showMakeReportVisibleModal = false;
          this.$store.dispatch('createSnackbar', snackbarMessage);
          this.$router.go(this.$router.currentRoute)
        });
      },
    },
    $trs: {
      reportVisibleToLearnersLabel: {
        message: 'Report visible to learners',
        context:
          'The label for a switch that will toggle whether or not learners can view their assessment report.',
      },
      openAssessmentLabel: {
        message: 'Assessment created',
        context: '',
      },
      closeAssessmentLabel: {
        message: 'Assessment started',
        context: '',
      },
      recipientsLabel: {
        message: 'Recipient',
        context: '',
      }
    },
  };

</script>


<style scoped lang="scss">

  .grid-item {
    font-size: 14px;

    @media print {
      font-size: inherit;
    }
  }

  .status-label {
    padding-bottom: 8px;
    font-weight: bold;

    @media print {
      padding-bottom: 0;
    }
  }

  .avg-score-info {
    margin-left: 8px;
  }

  .status-item {
    width: 100%;
    padding-top: 16px;

    @media print {
      padding-top: 10px;

      &:first-child {
        padding-top: 0;
      }
    }
  }

</style>
