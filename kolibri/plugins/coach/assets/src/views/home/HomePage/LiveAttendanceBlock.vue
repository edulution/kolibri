<template>

  <Block
    :allLinkText="viewAllString"
    :allLinkRoute="classRoute('ReportsAttendanceListPage')"
  >
    <KLabeledIcon slot="title">
      <KIcon slot="icon" people />
      {{ coachStrings.$tr('liveAttendanceLabel') }}
    </KLabeledIcon>

    <BlockItem class="block-item">
      <LiveAttendanceProgressDisplay
        :name="$tr('activeLearners')"
        :tally="liveAttendance.tally"
        :groupNames="liveAttendance.groups"
        :to="classRoute('ReportsAttendanceListPage')"
      />
    </BlockItem>
  </Block>

</template>


<script>

  import { crossComponentTranslator } from 'kolibri.utils.i18n';
  import commonCoach from '../../common';
  import Block from './Block';
  import BlockItem from './BlockItem';
  import LiveAttendanceProgressDisplay from './LiveAttendanceProgressDisplay';
  import ActivityBlock from './ActivityBlock';

  const translator = crossComponentTranslator(ActivityBlock);

  export default {
    name: 'LiveAttendanceBlock',
    components: {
      LiveAttendanceProgressDisplay,
      Block,
      BlockItem,
    },
    mixins: [commonCoach],
    $trs: {
      activeLearners: 'Live Learners',
    },
    computed: {
      liveAttendance() {
        const tallies = {
          active: this.activeLearners.length,
          notActive: this.learners.length - this.activeLearners.length,
        };
        return {
          tally: tallies,
          groups: [],
        };
      },
      viewAllString() {
        return translator.$tr('viewAll');
      },
    },
    methods: {
      // return the last activity among all users for a particular lesson
      lastActivity(lesson) {
        // Default to UNIX 0 so activity-less lessons go to the end of the list
        let last = new Date(0);
        if (!this.lessonLearnerStatusMap[lesson.id]) {
          return last;
        }
        Object.values(this.lessonLearnerStatusMap[lesson.id]).forEach(learner => {
          if (learner.last_activity > last) {
            last = learner.last_activity;
          }
        });
        return last;
      },
    },
  };

</script>


<style lang="scss" scoped></style>
