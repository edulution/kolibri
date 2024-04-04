<template>

  <KPageContainer
    style="padding-top: 24px;"
  >
    <BackLink
      :to="backlink"
      :text="backlinkLabel"
    />

    <!-- Cheating to get the same layout effect but not
           using a backlink...
      -->
    <HeaderWithOptions>
      <template #header>
        <div>
          <h1 class="exam-title">
            <!-- KLabeledIcon does not have an 'exam' token, but rather 'quiz' -->
            <KLabeledIcon
              :icon="examOrLesson === 'assessment' ? 'quiz' : 'lesson'"
              :label="assessmentTitle"
              class="assessment-title"
            />
          </h1>
          <StatusElapsedTime v-show="!$isPrint" :date="createdDate" actionType="created" />
        </div>
      </template>
      <template #options>
        <div>
          <slot name="dropdown"></slot>
        </div>
      </template>
    </HeaderWithOptions>
    <MissingResourceAlert v-if="resource.missing_resource" />

  </KPageContainer>

</template>


<script>

  import { mapState } from 'vuex';
  import MissingResourceAlert from 'kolibri-common/components/MissingResourceAlert';
  import HeaderWithOptions from './HeaderWithOptions';
  import StatusElapsedTime from './StatusElapsedTime';
  import BackLink from './BackLink';

  export default {
    name: 'AssessmentLessonDetailsHeader',
    components: {
      HeaderWithOptions,
      MissingResourceAlert,
      StatusElapsedTime,
      BackLink,
    },
    props: {
      backlink: {
        type: Object,
        required: true,
      },
      backlinkLabel: {
        type: String,
        required: true,
      },
      examOrLesson: {
        type: String,
        required: true,
        validator(value) {
          return ['lesson', 'assessment'].includes(value);
        },
      },
      assessmentTitle:{
          type: String,
          default:''
        },
        assessmentCreatedDate:{
          type: String,
          default:''
        }
    },
    computed: {
      ...mapState('classSummary', ['lessonMap', 'assessmentMap']),
      lesson() {
        return this.lessonMap[this.$route.params.lessonId] || {};
      },
      assessment() {
        return this.assessmentMap[this.$route.params.assessmentId] || {};
      },
      resource() {
        return this.examOrLesson === 'lesson' ? this.lesson : this.assessment;
      },
      createdDate() {
        if (this.assessmentCreatedDate) {
          return new Date(this.assessmentCreatedDate);
        } else {
          return null;
        }
      },
    },
  };

</script>


<style lang="scss" scoped>

  .exam-title {
    margin-bottom: 0;
    font-size: 1.5rem;
  }

  /deep/ .time-context {
    margin-bottom: 0;
  }

  .assessment-title {
    font-size: 20px;
  }

</style>
