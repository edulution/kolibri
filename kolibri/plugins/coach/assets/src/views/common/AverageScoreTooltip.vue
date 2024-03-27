<template>

  <CoreInfoIcon
    :tooltipText="tooltipMessage"
    :iconAriaLabel="tooltipMessage"
  />

</template>


<script>

  import CoreInfoIcon from 'kolibri.coreVue.components.CoreInfoIcon';

  export default {
    name: 'AverageScoreTooltip',
    components: {
      CoreInfoIcon,
    },
    props: {
      variant: {
        type: String,
        default: 'QUIZ',
      },
    },
    computed: {
      tooltipMessage() {
        if (this.variant === 'ASSESSMENT') {
          return this.$tr('visibleToLearnersTooltipMessageForAssessment')
        }
        return this.$tr('visibleToLearnersTooltipMessage')
      }
    },
    $trs: {
      visibleToLearnersTooltipMessage: {
        message: 'Calculated only from quizzes that were completed',
        context:
          'A message for a tooltip that shows when the user hovers over a small icon that tells the user that the Average Quiz Score is calculated only using quizzes that learners completed.',
      },
      visibleToLearnersTooltipMessageForAssessment: {
        message: 'Calculated only from assessments that were completed',
        context:
          'A message for a tooltip that shows when the user hovers over a small icon that tells the user that the Average Quiz Score is calculated only using quizzes that learners completed.',
      },
    },
  };

</script>
