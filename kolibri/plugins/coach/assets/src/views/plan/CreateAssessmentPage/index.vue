<template>
  <CoachImmersivePage
    :appBarTitle="$tr('createNewAssessmentLabel')"
    :authorized="userIsAuthorized"
    authorizedRole="adminOrCoach"
    icon="close"
    :pageTitle="$tr('createNewAssessmentLabel')"
    :route="toolbarRoute"
  >
    <KPageContainer>
      <h1>{{ $tr('createNewAssessmentLabel') }}</h1>

      <h2>{{ coachString('detailsLabel') }}</h2>

      <KGrid>
        <KGridItem :layout12="{ span: 5 }">
          <KTextbox
            v-model.trim="examTitle"
            :label="coachString('titleLabel')"
            :autofocus="true"
            :maxlength="100"
            type="text"
          />
        </KGridItem>

        <KGridItem :layout12="{ span: 5 }">
          <KSelect
            :value="selectedLearner"  
            :label="$tr('learnerLabel')"
            :options="learnerOptions"
            :style="{ background: $themePalette.grey.v_300 }"
            @change="onSelectLearner"
          />
        </KGridItem>
      </KGrid>

      <h2>{{ $tr('chooseExercises') }}</h2>

      <div>
        <div>
          <ul class="content-list">
            <li
              v-for="content in filteredContentList"
              :key="content.id"  
              class="content-list-item"
            >
              <KRadioButton
                v-model="selectedContent"
                :value="content.id"
                :showLabel="false"
                style="flex: 0;"
              />
              
              <div class="content-card" :style="{ backgroundColor: $themeTokens.surface }">
                <CardThumbnail
                  class="thumbnail"
                  :thumbnail="content.thumbnail"
                  :kind="content.kind"
                  :isMobile="windowIsSmall"
                />

                <div :class="windowIsSmall ? 'mobile-text' : 'text'" :style="{ color: $themeTokens.text }">
                  <div
                    :class="{ 'title-message-wrapper': Boolean(!windowIsSmall) }"
                    :style="{ color: $themeTokens.text }"
                  >
                    <h3
                      v-if="!windowIsSmall"
                      class="title"
                      dir="auto"
                    >
                      <KLabeledIcon :label="content.title">
                        <template #icon>
                          <ContentIcon :kind="content.kind" />
                        </template>
                      </KLabeledIcon>
                    </h3>
                    <h3
                      v-if="windowIsSmall"
                      dir="auto"
                    >
                      <KLabeledIcon :label="content.title">
                        <template #icon>
                          <ContentIcon :kind="content.kind" />
                        </template>
                      </KLabeledIcon>
                    </h3>
                  </div>

                  <TextTruncatorCss
                    v-if="!windowIsSmall"
                    :text="content.title"
                    :maxLines="3"
                    class="description"
                  />
                  
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <BottomAppBar>
        <KButtonGroup>
          <KButton
            :text="coreString('finishAction')"
            primary
            :disabled="isInvalidSubmission"
            @click="onSubmit"
          />
        </KButtonGroup>
      </BottomAppBar>
    </KPageContainer>
  </CoachImmersivePage>
</template>


<script>

import { AssessmentResource } from 'kolibri.resources';
  import { mapState, mapActions, mapGetters } from 'vuex';
  import responsiveWindowMixin from 'kolibri.coreVue.mixins.responsiveWindowMixin';
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import BottomAppBar from 'kolibri.coreVue.components.BottomAppBar';
  import ContentIcon from 'kolibri.coreVue.components.ContentIcon';
  import TextTruncatorCss from 'kolibri.coreVue.components.TextTruncatorCss';
  
  import CardThumbnail from '../LessonResourceSelectionPage/LessonContentCard/CardThumbnail.vue';
  import { PageNames } from '../../../constants/';
  import commonCoach from '../../common';
  import CoachImmersivePage from '../../CoachImmersivePage';

  export default {
    name: 'CreateAssessmentPage',
    components: {
      CoachImmersivePage,
      BottomAppBar,
      CardThumbnail,
      ContentIcon,
      TextTruncatorCss,
    },
    mixins: [commonCoreStrings, commonCoach, responsiveWindowMixin],
    data() {
      return {
        examTitle: '',
        selectedLearner: {},
        selectedContent: '',
      };
    },
    computed: {
      ...mapState(['toolbarRoute']),
      ...mapState('examCreation', [
        'contentList',
      ]),
      learnerOptions() {
        console.log({ learner: this.learners })

        return this.learners.map(learner => ({
          label: learner.name,
          value: learner.id
        }))
      },
      isInvalidSubmission() {
        if (!this.examTitle) {
          return true;
        }
        if (!Object.keys(this.selectedLearner).length) {
          return true;
        }
        if (!Object.keys(this.selectedContent).length) {
          return true;
        }
        return false;
      },
      filteredContentList() {
        return this.contentList;
      },
    },
    watch: {
    },
    methods: {
      onSelectLearner(option) {
        this.selectedLearner = option;
      },
      onSubmit() {
        const exam = {
          collection: this.classId,
          title: this.examTitle,
          seed: 928,
          question_count: 10,
          question_sources: [],
          assignments: [this.classId],
          learners_see_fixed_order: false,
          date_archived: null,
          date_activated: null,
          learner_ids: [this.selectedLearner.value],
        };
        return AssessmentResource.saveModel({ data: exam }).then(() => {
          return this.$router.push({ name: PageNames.ASSESSMENTS });
        });
      }
    },
    $trs: {
      learnerLabel: {
        message: 'Learner',
        context: '',
      },
      resources: {
        message: '{count} {count, plural, one {resource} other {resources}}',
        context: "Only translate 'resource' and 'resources'.",
      },
      createNewAssessmentLabel: {
        message: 'Create new assessment',
        context: "Title of the screen launched from the 'New quiz' button on the 'Plan' tab.",
      },
      chooseExercises: {
        message: 'Select channel to map assessment',
        context:
          'When creating a new quiz, coaches can choose which folders or exercises they want to include in the quiz from the channels that contain exercise resources.',
      },
      noneSelected: {
        message: 'No exercises are selected',
        context:
          "Error message which displays if no resources have been selected in the 'Create new quiz' screen.",
      },
      exitSearchButtonLabel: {
        message: 'Exit search',
        context:
          "Button to exit the 'Search' page when user searches for resources to use in a quiz.",
      },
      selectionInformation: {
        message:
          '{count, number, integer} of {total, number, integer} {total, plural, one {resource selected} other {resources selected}}',

        context:
          "Indicates the number of resources selected by the coach. For example: '3 of 5 resources selected'.\n\nOnly translate 'of' and 'resource/resources selected'",
      },
    },
  };

</script>


<style lang="scss" scoped>
  @import '~kolibri-design-system/lib/styles/definitions';
  $ratio: 16 / 9;

  $thumb-height: 125px;
  $thumb-width: round($thumb-height * $ratio);
  $checkbox-offset: 42px;

  $mobile-thumb-width: 60px;
  $mobile-thumb-height: round($thumb-width / $ratio);

  .search-box {
    display: inline-block;
    vertical-align: middle;
  }

  .bookmarks-container {
    display: flex;
    align-items: center;
  }

  .lesson-content-card {
    width: 100%;
  }

  .bookmark-container {
    display: flex;
    min-height: 141px;
    margin-bottom: 24px;
    border-radius: 2px;
    box-shadow: 0 1px 5px 0 #a1a1a1, 0 2px 2px 0 #e6e6e6, 0 3px 1px -2px #ffffff;
    transition: box-shadow 0.25s ease;
  }

  .bookmark-container:hover {
    box-shadow: 0 5px 5px -3px #a1a1a1, 0 8px 10px 1px #d1d1d1, 0 3px 14px 2px #d4d4d4;
  }

  .text {
    margin-left: 15rem;
  }

  .content-list {
    display: block;
    padding: 0;
    list-style: none;
  }

  .content-list-item {
    position: relative;
    display: flex;
    text-align: right;
    gap: 15px;
  }

  .content-checkbox {
    position: absolute;
    top: 34%; // offset accouting for shadow on card
    left: 0;
    display: inline-block;
  }

  // content card css
  .content-card {
    flex: 1;
    @extend %dropshadow-2dp;

    position: relative;
    display: block;
    min-height: $thumb-height + 16;
    padding: 16px;
    margin-bottom: 24px;
    text-align: left;
    text-decoration: none;
    border-radius: 2px;
    transition: box-shadow $core-time ease;

    &:hover,
    &:focus {
      @extend %dropshadow-8dp;
    }
  }

  .thumbnail {
    position: absolute;
    top: 0;
    left: 0;
    margin: 8px;
  }

  .text {
    flex-direction: column;
    margin-left: $thumb-width + 8;
  }

  .mobile-text {
    margin-left: $mobile-thumb-width + 8;
  }

  .title-message-wrapper {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  .title,
  .message {
    margin-top: 0;
    overflow: hidden;
  }

  .message {
    text-align: right;
  }

  .coach-content-label {
    margin: 8px 0;
  }
  // content card css

  .with-checkbox {
    margin-left: $checkbox-offset;
  }

</style>
