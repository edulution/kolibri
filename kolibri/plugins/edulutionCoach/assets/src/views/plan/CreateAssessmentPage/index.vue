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
            v-model="assessmentTitle"
            :label="coachString('titleLabel')"
            :maxlength="100"
            type="text"
          />
        </KGridItem>

        <KGridItem :layout12="{ span: 5 }">
          <KSelect
            v-model="selectedLearner"
            :label="$tr('learnerLabel')"
            :options="learnerOptions"
            :style="{ background: $themePalette.grey.v_300, padding: '10px 10px 10px 10px' }"
          />
        </KGridItem>
      </KGrid>

      <h2 v-if="toggleTable === 'SHOW_CHANNEL'">{{ $tr('chooseChannel') }}</h2>

      <div v-if="toggleTable === 'SHOW_CHANNEL'">
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
              
              <div 
                class="content-card" 
                :style="{ backgroundColor: $themeTokens.surface }"
              >
                <CardThumbnail
                  class="thumbnail"
                  :thumbnail="content.thumbnail"
                  :kind="content.kind"
                  :isMobile="windowIsSmall"
                />

                <div
                  :class="windowIsSmall ? 'mobile-text' : 'text'"
                  :style="{ color: $themeTokens.text }"
                >
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

      <h2 v-if="toggleTable === 'SHOW_TABLE'">Configure weightage for assessment</h2>
      <ChannelTable 
        v-if="toggleTable === 'SHOW_TABLE'"
        :tableData="tableData"
        :newData="newData"
        @update-new-data="updateNewData"
      />

      <BottomAppBar>
        <KButtonGroup>
          <KButton
            v-if="toggleTable === 'SHOW_TABLE'"
            :text="coreString('finishAction')"
            primary
            :disabled="isInvalidSubmission"
            @click="onSubmit"
          />
          <KButton
            v-if="toggleTable === 'SHOW_CHANNEL'"
            :text="$tr('continueLabel')"
            primary
            :disabled="isInvalidSubmission"
            @click="onSelectChannel"
          />
        </KButtonGroup>
      </BottomAppBar>
    </KPageContainer>
  </CoachImmersivePage>
</template>


<script>

  import { mapState } from 'vuex';
  
  import { AssessmentResource, ContentNodeResource } from 'kolibri.resources';
  import responsiveWindowMixin from 'kolibri.coreVue.mixins.responsiveWindowMixin';
  
  import BottomAppBar from 'kolibri.coreVue.components.BottomAppBar';
  import ContentIcon from 'kolibri.coreVue.components.ContentIcon';
  import TextTruncatorCss from 'kolibri.coreVue.components.TextTruncatorCss';
  
  import { ContentNodeKinds } from 'kolibri.coreVue.vuex.constants';
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  
  import CardThumbnail from '../LessonResourceSelectionPage/LessonContentCard/CardThumbnail.vue';
  import CoachImmersivePage from '../../CoachImmersivePage';
  
  import { PageNames } from '../../../constants';
  import commonCoach from '../../common';
  import ChannelTable from './ChannelTable.vue';

  export default {
    name: 'CreateAssessmentPage',
    components: {
      CoachImmersivePage,
      BottomAppBar,
      CardThumbnail,
      ContentIcon,
      TextTruncatorCss,
      ChannelTable
    },
    mixins: [commonCoreStrings, commonCoach, responsiveWindowMixin],
    data() {
      return {
        assessmentTitle: '',
        selectedLearner: {},
        selectedContent: '',
        toggleTable:'SHOW_CHANNEL',
        tableData:[],
        newData:[]
      };
    },
    computed: {
      ...mapState(['toolbarRoute']),
      ...mapState('examCreation', [
        'contentList',
      ]),
      ...mapState({
        userId: state => state.core.session.user_id,
      }),
      learnerOptions() {
        return this.learners.map(learner => ({
          label: learner.name,
          value: learner.id
        }))
      },
      isInvalidSubmission() {
        if (!this.assessmentTitle) {
          return true;
        }
        if (!Object.keys(this.selectedLearner).length) {
          return true;
        }
        if (!this.selectedContent) {
          return true;
        }
        return false;
      },
      filteredContentList() {
        return this.contentList;
      },
    },
    methods: {
      async prepareAssessments() {
        const assessments = [];
        const contentNodes = await ContentNodeResource.fetchCollection({
          getParams: {
            parent: this.selectedContent,
            kind_in: [ContentNodeKinds.TOPIC]
          }
        })

        const descendantsNodes = await ContentNodeResource.fetchDescendantsAssessments(
          contentNodes.map(c => c.id)
        );
        
        for (const contentNode of contentNodes) {
          const descendantsNodeIndex = descendantsNodes.data.findIndex(
            d => d.id === contentNode.id && d.num_assessments
          )
          if (descendantsNodeIndex !== -1) {
            const excercises = await ContentNodeResource.fetchDescendants([contentNode.id], {
              descendant_kind: ContentNodeKinds.EXERCISE,
            })

            const exerciseContents = await ContentNodeResource.fetchCollection({
              getParams: {
                ids: excercises.data.map(e => e.id),
              }
            })
            
            let questionSources = [];

            for (const exercise of exerciseContents) {
              questionSources = [
                ...questionSources,
                ...exercise.assessmentmetadata.assessment_item_ids.map(a => ({
                  exercise_id: exercise.id,
                  question_id: a,
                  title: exercise.title,
                  missing_resource: false,
                }))
              ]
            }
            
            assessments.push({
              id: contentNode.id,
              title: contentNode.title,
              content_id: contentNode.content_id,
              limit: questionSources.length,
              exercises: excercises.data.map(e => ({
                id: e.id,
                title: e.title,
                weightage: questionSources.filter(i => i.exercise_id === e.id).length
              })),
              question_sources: questionSources,
              question_count: questionSources.length,
            })
          }
        }
        return assessments;
      },
      async onSubmit() {

        for (let i = 0; i < this.tableData.length; i++) {

        const tableDataItem = this.tableData[i]

        const matchingNewItem = this.newData.find(item => item.id === tableDataItem.id);

        if (matchingNewItem) {
          tableDataItem.limit = matchingNewItem.value;
          tableDataItem.exercises = tableDataItem.exercises.map(ex => {
            const exI = matchingNewItem.exercises.find(d => d.id === ex.id)
            return {
              ...ex,
              weightage: exI.value
            }
          })
        }
      }

        const data = {
          collection: this.classId,
          title: this.assessmentTitle,
          date_archived: null,
          date_activated: null,
          channel_id: this.selectedContent,
          learner_id: this.selectedLearner.value,
          assessments: [...this.tableData.reverse()],
          creator_id: this.userId,
        };

        try {
          const result = await AssessmentResource.saveModel({ data })
          console.log({ result })
          this.$router.push({ name: PageNames.ASSESSMENTS });
        } catch (error) {
          if (error?.response?.data?.error) {
            this.$store.dispatch('createSnackbar', error.response.data.error);
          }
        }
      },
        // @public
      async onSelectChannel() {
        this.toggleTable = 'SHOW_TABLE'
        const assessments = await this.prepareAssessments();
        this.tableData = assessments
      },
      updateNewData(newData) {
        this.newData = newData; 
      },
    },
    $trs: {
      learnerLabel: {
        message: 'Learner',
        context: '',
      },
      createNewAssessmentLabel: {
        message: 'Create new assessment',
        context: "Title of the screen launched from the 'New quiz' button on the 'Plan' tab.",
      },
      chooseChannel: {
        message: 'Select channel to map assessment',
        context:
          'When creating a new quiz, coaches can choose which folders or exercises they want to include in the quiz from the channels that contain exercise resources.',
      },
      continueLabel: {
        message: 'Continue',
        context: '',
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
