<template>
  <CoachAppBarPage
    :authorized="userIsAuthorized"
    authorizedRole="adminOrCoach"
    :showSubNav="true"
  >
    <KGrid gutter="16">
      <KGridItem>
        <OverviewBlock />
      </KGridItem>
      <KGridItem :layout12="{ span: 6 }">
        <KGrid gutter="16">
          <KGridItem>
            <QuizzesBlock />
          </KGridItem>
          <KGridItem>
            <LessonsBlock />
          </KGridItem>
        </KGrid>
      </KGridItem>
      <KGridItem :layout12="{ span: 6 }">
        <KGrid gutter="16">
          <KGridItem>
            <AssessmentBlock />
          </KGridItem>
          <KGridItem>
            <AttendanceBlock />
          </KGridItem>
          <KGridItem>
            <ActivityBlock />
          </KGridItem>
        </KGrid>
      </KGridItem>
    </KGrid>
  </CoachAppBarPage>
</template>


<script>

  import CoachAppBarPage from '../../CoachAppBarPage';
  import commonCoach from '../../common';
  import OverviewBlock from './OverviewBlock';
  import ActivityBlock from './ActivityBlock';
  import LessonsBlock from './LessonsBlock';
  import QuizzesBlock from './QuizzesBlock';
  import AttendanceBlock from './AttendanceBlock';
  import AssessmentBlock from './AssessmentBlock.vue';

  export default {
    name: 'HomePage',
    components: {
    CoachAppBarPage,
    OverviewBlock,
    ActivityBlock,
    LessonsBlock,
    QuizzesBlock,
    AttendanceBlock,
    AssessmentBlock
},
    mixins: [commonCoach],
  };

</script>


<style lang="scss" scoped>

  .new-coach-block {
    min-width: 0;
  }

</style>
