<template>

  <div>
    <h2>
      <KLabeledIcon
        icon="quiz"
        :label="header"
      />
    </h2>

    <CardGrid
      v-if="visibleQuizzes.length > 0"
      :gridType="1"
    >
      <AssessmentCard
        v-for="quiz in visibleQuizzes"
        :key="quiz.id"
        :quiz="quiz"
        :to="getClassAssessmentLink(quiz)"
        :collectionTitle="displayClassName ? getAssessmentName(quiz) : ''"
      />
    </CardGrid>
    <p v-else>
      {{ $tr('noAssessmentMessage') }}
    </p>

  </div>

</template>


<script>

  import { computed } from 'kolibri.lib.vueCompositionApi';
  import useLearnerResources from '../../composables/useLearnerResources';
  import CardGrid from '../cards/CardGrid';
  import AssessmentCard from '../cards/AssessmentCard';

  export default {
    name: 'AssessmentCards',
    components: {
      CardGrid,
      AssessmentCard
    },
    setup(props) {
      const { getClass, getClassAssessmentLink } = useLearnerResources();
      const visibleQuizzes = computed(() => {
        if (!props.quizzes) {
          return [];
        }
        return props.quizzes.filter(assessment => {
          if (!assessment.active) {
            return false;
          } else if (assessment.archive) {
            // Closed (archived) quizzes only show if the learner started/submitted
            return assessment.progress.started || assessment.progress.closed;
          } else {
            return true;
          }
        });
      });

      function getAssessmentName(assessment) {
        const assessmentClass = getClass(assessment.collection);
        return assessmentClass ? assessmentClass.name : '';
      }

      return {
        visibleQuizzes,
        getAssessmentName,
        getClassAssessmentLink,
      };
    },
    props: {
      // `quizzes` prop is used in `setup`
      // eslint-disable-next-line kolibri/vue-no-unused-properties
      quizzes: {
        type: Array,
        required: true,
      },
      /**
       * If `true` 'Recent quizzes' header will be displayed.
       * Otherwise 'Your quizzes' will be displayed.
       */
      recent: {
        type: Boolean,
        default: false,
      },
      /**
       * A quiz's class name will be displayed above
       * the quiz title if `true`
       */
      displayClassName: {
        type: Boolean,
        default: false,
      },
    },
    computed: {
      // TODO: Would be more consistent to have this computed property in `setup`,
      // however haven't found a way to work with translations there yet
      header() {
        return this.recent ? this.$tr('recentAssessmentsHeader') : this.$tr('yourAssessmentHeader');
      },
    },
    $trs: {
      yourAssessmentHeader: {
        message: 'Your assessments',
        context:
          "AssessmentCards.yourAssessmentHeader\n\nHeading on the 'Learn' page for a section where a learner can see which assessments have been assigned to them.",
      },
      noAssessmentMessage: {
        message: 'You have no assessments assigned',
        context: 'Message that a learner sees if a coach has not assigned any assessments to them.',
      },
      recentAssessmentsHeader: {
        message: 'Recent assessments',
        context:
          "Section header on the learner's Home page, displaying the most recent assessments that the coaches assigned to them.",
      },
    },
  };

</script>


<style lang="scss" scoped></style>
