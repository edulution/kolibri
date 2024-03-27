<template>

  <Block
    :allLinkText="coachString('viewAllAction')"
    :allLinkRoute="classRoute('ReportsAssessmentListPage', {})"
    :showAllLink="table.length > 0"
  >
    <template #title>
      <KLabeledIcon icon="quiz" :label="coreString('assessmentLabel')" />
    </template>
  
    <p v-if="table.length === 0">
      {{ coachString('quizListEmptyState') }}
    </p>
  
    <BlockItem
      v-for="tableRow in table"
      :key="tableRow.key"
    >
      <ItemProgressDisplay
        :name="tableRow.name"
        :tally="tableRow.tally"
        :groupNames="groupAndAdHocLearnerNames(tableRow.groups, tableRow.assignments)"
        :hasAssignments="tableRow.hasAssignments"
        :to="classRoute('ReportsAssessmentLearnerListPage', { quizId: tableRow.key })"
      />
    </BlockItem>
  </Block>
  
</template>
  
  
  <script>
  
    import orderBy from 'lodash/orderBy';
    import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
    import commonCoach from '../../common';
    import Block from './Block';
    import BlockItem from './BlockItem';
    import ItemProgressDisplay from './ItemProgressDisplay';
  
    const MAX_QUIZZES = 3;
  
    export default {
      name: 'AssessmentBlock',
      components: {
        ItemProgressDisplay,
        Block,
        BlockItem,
      },
      mixins: [commonCoach, commonCoreStrings],
      computed: {
        table() {
          const recent = orderBy(this.assessments, this.lastActivity, ['desc']).slice(0, MAX_QUIZZES);
          return recent.map(assessment => {
            const assigned = this.getLearnersForExam(assessment);
            return {
              key: assessment.id,
              name: assessment.title,
              tally: this.getExamStatusTally(assessment.id, assigned),
              groups: assessment.groups.map(groupId => this.groupMap[groupId].name),
              assignments: assessment.assignments,
              hasAssignments: assigned.length > 0,
            };
          });
        },
      },
      methods: {
        // return the last activity among all users for a particular exam
        lastActivity(exam) {
          // Default to UNIX 0 so activity-less exams go to the end of the list
          let last = new Date(0);
          if (!this.examLearnerStatusMap[exam.id]) {
            return last;
          }
          Object.values(this.examLearnerStatusMap[exam.id]).forEach(status => {
            if (status.last_activity > last) {
              last = status.last_activity;
            }
          });
          return last;
        },
        groupAndAdHocLearnerNames(groups, assignments) {
          const adHocGroup = this.adHocGroups.find(group => assignments.includes(group.id));
          let adHocLearners = [];
          if (adHocGroup) {
            adHocLearners = adHocGroup.member_ids.map(learnerId => this.learnerMap[learnerId].name);
          }
          return groups.concat(adHocLearners);
        },
      },
    };
  
  </script>
  
  
  <style lang="scss" scoped></style>
  