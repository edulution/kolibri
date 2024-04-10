<template>

  <Block
    :allLinkText="coachString('viewAllAction')"
    :allLinkRoute="classRoute('ReportsAttendanceListPage')"
    :showAllLink="true"
  >
    <template #title>
      <KLabeledIcon icon="people" :label="$tr('liveAttendanceLabel')" />
    </template>

    <BlockItem>
      <LiveAttendanceProgressDisplay
        :name="$tr('activeLearners')"
        :tally="liveAttendance.tally"
        :groupNames="liveAttendance.groups"
      />
    </BlockItem>
  </Block>
  
</template>
  
  
<script>
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import commonCoach from '../../common';
  import Block from './Block';
  import BlockItem from './BlockItem';
  import LiveAttendanceProgressDisplay from './LiveAttendanceProgressDisplay';

  export default {
    name: 'AttendanceBlock',
    components: {
      Block,
      BlockItem,
      LiveAttendanceProgressDisplay
    },
    mixins: [commonCoach, commonCoreStrings],
    computed: {
      liveAttendance() {
        const tallies = {
          active: this.activeLearners?.length,
          notActive: this.learners.length - this.activeLearners?.length,
        };
        return {
          tally: tallies,
          groups: [],
        };
      },
    },
    methods: {},
    $trs: {
      activeLearners: {
        message: 'Live Learners',
        context:
          "Refers to the section within the 'Class home' tab which provides real time notifications of what's happening with the learners in a class. \n\nCoaches can track learners' progress here.",
      },
      liveAttendanceLabel:{
        message:"Live Attendance",
        context:"Live",
      }
    }
  };

</script>
  
  
<style lang="scss" scoped></style>
  