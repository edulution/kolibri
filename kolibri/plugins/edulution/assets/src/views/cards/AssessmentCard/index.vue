<template>

  <BaseCard
    v-if="assessment"
    v-bind="{ to, title, collectionTitle, completedLabel, inProgressLabel }"
  >
    <template
      v-if="showThumbnail"
      #topLeft
    >
      <QuizThumbnail rounded />
    </template>
  </BaseCard>
  
</template>
  
  
  <script>
  
    import QuizThumbnail from '../../thumbnails/QuizThumbnail';
    import BaseCard from '../BaseCard';
  
    export default {
      name: 'AssessmentCard',
      components: {
        BaseCard,
        QuizThumbnail,
      },
      props: {
        assessment: {
          type: Object,
          required: true,
        },
        /**
         * vue-router link object
         */
        to: {
          type: Object,
          required: true,
        },
        collectionTitle: {
          type: String,
          required: false,
          default: '',
        },
        showThumbnail: {
          type: Boolean,
          required: false,
          default: false,
        },
      },
      computed: {
        progress() {
          return this.assessment ? this.assessment.progress : undefined;
        },
        title() {
          return this.assessment ? this.assessment.title : '';
        },
        inProgressLabel() {
          if (!this.progress) {
            return '';
          }
          const { started, closed, answer_count } = this.progress;
          const { question_count } = this.assessment;
          if (started && !closed) {
            return this.$tr('questionsLeft', {
              questionsLeft: Math.max(0, question_count - answer_count),
            });
          }
          return '';
        },
        completedLabel() {
          if (!this.progress) {
            return '';
          }
          const { score, closed } = this.progress;
          const { question_count } = this.assessment;
          if (closed) {
            let percentage = 0;
            const nCorrect = Number(score);
            if (nCorrect > 0) {
              percentage = Math.round(100 * (nCorrect / question_count));
            }
            return this.$tr('completedPercentLabel', { score: percentage });
          }
          return '';
        },
      },
      $trs: {
        questionsLeft: {
          message:
            '{questionsLeft, number, integer} {questionsLeft, plural, one {question} other {questions}} left',
          context: 'Indicates how many questions the learner has left to complete.',
        },
        completedPercentLabel: {
          message: 'Score: {score, number, integer}%',
          context: 'A label shown to learners on a Assessment card when the assessment is completed',
        },
      },
    };
  
  </script>
  
  
  <style lang="scss" scoped></style>
  