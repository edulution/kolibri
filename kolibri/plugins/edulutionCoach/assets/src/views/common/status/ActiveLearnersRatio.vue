<template>
  <div :class="progressClassName">
    <KLabeledIcon nowrap>
      <template #icon>
        <CoachStatusIcon ref="status" :icon="icon" />
      </template>
      {{ text }}
    </KLabeledIcon>
    <KTooltip
      v-if="false"
      reference="status"
      placement="top"
      :refs="$refs"
    >
      {{ tooltip }}
    </KTooltip>
  </div>

</template>
  
  
  <script>
    import { coachStringsMixin } from '../commonCoachStrings';
    import CoachStatusIcon from './CoachStatusIcon';
    import { statusStringsMixin, isValidVerb } from './statusStrings';
  
    export default {
      name: 'ActiveLearnersRatio',
      components: {
        CoachStatusIcon,
      },
      mixins: [statusStringsMixin, coachStringsMixin],
      props: {
        verb: {
          type: String,
          required: true,
          validator: isValidVerb,
        },
        icon: {
          type: String,
          required: true,
        },
      },
      computed: {
        strings() {
          return this.activeLearnersTranslators[this.verb];
        },
        text() {
          if (!this.verbosityNumber) {
            return this.coachStrings('ratioShort', { value: this.count, total: this.total });
          }
          if (this.count === this.total && this.total > 2 && this.verb != 'notStarted') {
            return this.strings.$tr(this.shorten('allOfMoreThanTwo', this.verbosityNumber), {
              total: this.total,
            });
          }
          return this.strings.$tr(this.shorten('ratio', this.verbosityNumber), {
            count: this.count,
            total: this.total,
          });
        },
        tooltip() {
          return this.strings.$tr(this.shorten('ratio', 2), {
            count: this.count,
            total: this.total,
          });
        },
        progressClassName() {
          if (this.count === this.total) {
            return 'progress-completed'
          }
          if (this.count < this.total) {
            return 'progress-inprogress'
          }
          return 'progress-default'
        }
      },
    };
  
  </script>
  
  
  <style lang="scss" scoped>
  .progress-inprogress svg {
    fill: orange !important;
  }
  .progress-completed svg {
    fill: green !important;
  }
  .progress-default svg {
    fill: #071d49 !important
  }
</style>
  