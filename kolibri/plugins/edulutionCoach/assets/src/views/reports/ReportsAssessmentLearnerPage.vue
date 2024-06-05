<template>

  <CoachImmersivePage
    :appBarTitle="exam.title"
    :authorized="userIsAuthorized"
    authorizedRole="adminOrCoach"
    icon="back"
    :primary="false"
    :route="toolbarRoute"
  >
    <LearnerAssessmentReport @navigate="handleNavigation" />
  </CoachImmersivePage>
  
</template>
  
  
  <script>
  
    import { mapState } from 'vuex';
    import commonCoach from '../common';
    import CoachImmersivePage from '../CoachImmersivePage';
    import LearnerAssessmentReport from '../common/LearnerAssessmentReport';
  
    export default {
      name: 'ReportsAssessmentLearnerPage',
      components: {
        CoachImmersivePage,
        LearnerAssessmentReport,
      },
      mixins: [commonCoach],
      computed: {
        ...mapState('examReportDetail', ['exam']),
        toolbarRoute() {
          const backRoute = this.backRouteForQuery(this.$route.query);
          const assessmentGroupId = this.$route.query.assessmentGroupId || ''
          return backRoute || this.classRoute('ReportsAssessmentLearnerListPage', { quizId: assessmentGroupId });
        },
      },
      methods: {
        handleNavigation(params) {
          this.$router.push({
            name: this.name,
            params: {
              classId: this.$route.params.classId,
              ...params,
            },
            query: this.$route.query,
          });
        },
      },
    };
  
  </script>
  
  
  <style lang="scss" scoped></style>
  