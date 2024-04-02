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
          :backlink="classRoute('ReportsAssessmentListPage')"
          :backlinkLabel="coachString('allAssessmentsLabel')"
          optionsFor="report"
          :assessmentTitle="assessmentDetails.title"
        />
      </KGridItem>

      <KGridItem :layout12="{ span: $isPrint ? 12 : 4 }">
        <h2 class="visuallyhidden">
          {{ coachString('generalInformationLabel') }}
        </h2>
        <AssessmentStatus
          :className="className"
          :groupAndAdHocLearnerNames="getRecipientNameForAssessment(assessmentDetails)"
          :exam="assessmentDetails"
          showReportVisible="true"
          variant="REPORT"
        />
      </KGridItem>

      <KGridItem :layout12="{ span: $isPrint ? 12 : 8 }">
        <h2 class="visuallyhidden">
          {{ coachString('detailsLabel') }}
        </h2>
        <KPageContainer :topMargin="$isPrint ? 0 : 16">
          <ReportsControls @export="$emit('export')" />
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
  import ReportsControls from './ReportsControls';

  export default {
    name: 'ReportsAssessmentBaseListPage',
    components: {
      CoachAppBarPage,
      ReportsControls,
    },
    mixins: [commonCoach, commonCoreStrings],
    props: {
      assessmentDetails: {
        type: Object,
        required: true,
      }
    },
  };

</script>


<style lang="scss" scoped>

  @import '../common/three-card-layout';

</style>
