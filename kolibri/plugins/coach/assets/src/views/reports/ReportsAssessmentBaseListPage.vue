<template>

  <CoachAppBarPage
    :authorized="userIsAuthorized"
    authorizedRole="adminOrCoach"
    :showSubNav="true"
  >

    <KGrid gutter="16">
      <KGridItem>
        <AssessmentLessonDetailsHeader
          examOrLesson="exam"
          :backlink="
            group ? classRoute('ReportsGroupReportPage') : classRoute('ReportsAssessmentListPage')"
          :backlinkLabel="group ? group.name : coachString('allAssessmentsLabel')"
          optionsFor="report"
        >
          <template #dropdown>
            <QuizOptionsDropdownMenu
              optionsFor="assessment"
              @select="handleSelectOption"
            />
          </template>
        </AssessmentLessonDetailsHeader>
      </KGridItem>
      <KGridItem :layout12="{ span: $isPrint ? 12 : 4 }">
        <h2 class="visuallyhidden">
          {{ coachString('generalInformationLabel') }}
        </h2>
        <AssessmentStatus
          :className="className"
          :avgScore="avgScore"
          :groupAndAdHocLearnerNames="getRecipientNamesForExam(exam)"
          :exam="exam"
          showReportVisible="true"
          showSize="true"
        />
      </KGridItem>
      <KGridItem :layout12="{ span: $isPrint ? 12 : 8 }">
        <h2 class="visuallyhidden">
          {{ coachString('detailsLabel') }}
        </h2>
        <KPageContainer :topMargin="$isPrint ? 0 : 16">
          <ReportsControls @export="$emit('export')" />
          <HeaderTabs :enablePrint="true">
            <HeaderTab
              :text="coachString('resultBreakdownLabel')"
              :to="group ?
                classRoute('ReportsGroupReportAssessmentLearnerListPage') :
                classRoute('ReportsAssessmentLearnerListPage')
              "
            />
          </HeaderTabs>
          <slot></slot>
        </KPageContainer>
      </KGridItem>
    </KGrid>
  </CoachAppBarPage>

</template>


<script>

  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import commonCoach from '../common';
  import CoachAppBarPage from '../CoachAppBarPage';
  import QuizOptionsDropdownMenu from '../plan/QuizSummaryPage/QuizOptionsDropdownMenu';
  import ReportsControls from './ReportsControls';

  export default {
    name: 'ReportsAssessmentBaseListPage',
    components: {
      CoachAppBarPage,
      ReportsControls,
      QuizOptionsDropdownMenu,
    },
    mixins: [commonCoach, commonCoreStrings],
    computed: {
      avgScore() {
        return this.getExamAvgScore(this.$route.params.quizId, this.recipients);
      },
      exam() {
        return this.examMap[this.$route.params.quizId];
      },
      recipients() {
        return this.getLearnersForExam(this.exam);
      },
      group() {
        return this.$route.params.groupId && this.groupMap[this.$route.params.groupId];
      },
    },
    methods: {
      handleSelectOption(option) {
        if (option === 'EDIT_DETAILS') {
          this.$router.push(this.$router.getRoute('QuizReportEditDetailsPage'));
        }
        if (option === 'PREVIEW') {
          this.$router.push(
            this.$router.getRoute('ReportsAssessmentPreviewPage', {}, this.defaultBackLinkQuery)
          );
        }
        if (option === 'PRINT_REPORT') {
          this.$print();
        }
        if (option === 'EXPORT') {
          this.$emit('export');
        }
      },
    },
  };

</script>


<style lang="scss" scoped>

  @import '../common/three-card-layout';

</style>
