<template>

  <KGrid class="wrapper">
    <KGridItem :layout12="{ span: 9 }">
      <h3 class="title">
        {{ name }}
      </h3>
    </KGridItem>

    <KGridItem :layout12="{ span: 3 }" alignment="left">
      <div class="context">
        <Recipients :groupNames="groupNames" />
      </div>
    </KGridItem>

    <KGridItem :layout12="{ span: 12 }">
      <ActiveLearnerSummaryBar
        :tally="tally"
        class="dashboard-bar"
      />
    </KGridItem>

    <KGridItem :layout12="{ span: 12 }">
      <StatusSummaryActiveLearners
        :tally="tally"
      />
    </KGridItem>
  </KGrid>

</template>


<script>

  import commonCoach from '../../common';
  import ActiveLearnerSummaryBar from '../../common/status/ActiveLearnerSummaryBar';
  import StatusSummaryActiveLearners from '../../common/status/StatusSummaryActiveLearners';

  export default {
    name: 'LiveAttendanceProgressDisplay',
    components: {
      ActiveLearnerSummaryBar,
      StatusSummaryActiveLearners,
    },
    mixins: [commonCoach],
    props: {
      name: {
        type: String,
        required: true,
      },
      groupNames: {
        type: Array,
        required: true,
      },
      tally: {
        type: Object,
        required: true,
      },
    },
  };

</script>


<style lang="scss" scoped>

  .title {
    margin-bottom: 0;
  }

  .context {
    position: relative;
    top: 16px;
    margin-bottom: 16px;
    font-size: small;
    text-align: right;
  }

  .dashboard-bar {
    width: 100%;
    height: 16px;
    margin-top: 8px;
    margin-bottom: 8px;
  }

  .progress {
    position: absolute;
    bottom: 0;
    font-size: 14px;
  }

  .progress.completed {
    left: 0;
  }

  .progress.help {
    right: -12px;
  }

  .link {
    text-decoration: none;
  }

  .wrapper {
    margin-bottom: 8px;
  }

</style>
