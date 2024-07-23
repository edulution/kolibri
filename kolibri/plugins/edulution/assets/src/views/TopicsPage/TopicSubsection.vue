<template>

  <div>
    <div class="topic-subsection-wrapper" :class="[{ 'topic-subsection-expanded': topicExpanded }]">
      <div
        class="topic-subsection-header"
        :style="{ backgroundColor: $themeTokens.appBar }"
        @click="onExpansionClick"
      >
        <!-- header link to folder -->
        <img
          v-if="topic.thumbnail"
          :src="topic.thumbnail"
          :alt="topic.title"
          class="topic-logo"
        >
        <h2>
          {{ topic.title }}
        </h2>

        <div style="flex-grow: 1;"></div>

        <KIcon
          icon="chevronDown"
          :style="{ top: '4px' }"
        />
        
        <div class="progress-bar-wrapper" :style="{ backgroundColor: $themePalette.grey.v_300 }">
          <div
            class="progress-bar"
            :style="{
              width: percent + '%',
              backgroundColor: $themePalette.orange.v_400
            }"
          >

          </div>
        </div>
      </div>
      
      <div class="topic-subsection-body">
        <!-- card grid of items in folder -->
        <LibraryAndChannelBrowserMainContent
          v-if="topic.children && topic.children.length"
          data-test="children-cards-grid"
          :contents="topic.children"
          :topicKnowledgemap="topicKnowledgemap"
          :allowDownloads="allowDownloads"
          currentCardViewStyle="card"
          :keepCurrentBackLink="true"
          @toggleInfoPanel="$emit('toggleInfoPanel', $event)"
        />
        <KButton
          v-if="topic.showMore"
          class="more-after-grid"
          data-test="more-button"
          appearance="basic-link"
          @click="$emit('showMore', topic.id)"
        >
          {{ coreString('showMoreAction') }}
        </KButton>
        <KRouterLink v-else-if="topic.viewAll" class="more-after-grid" :to="topic.viewAll">
          {{ coreString('viewAll') }}
        </KRouterLink>
        <KButton
          v-else-if="topic.viewMore && topic.id !== subTopicLoading"
          class="more-after-grid"
          appearance="basic-link"
          @click="$emit('loadMoreInSubtopic', topic.id)"
        >
          {{ coreString('viewMoreAction') }}
        </KButton>

        <KCircularLoader v-if="topic.id === subTopicLoading" />
      </div>
    </div>
  </div>

</template>


<script>

  import get from 'lodash/get'
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import useContentLink from '../../composables/useContentLink';
  import LibraryAndChannelBrowserMainContent from '../LibraryAndChannelBrowserMainContent';

  export default {
    name: 'TopicSubsection',
    components: { LibraryAndChannelBrowserMainContent },
    mixins: [commonCoreStrings],
    setup() {
      const { genContentLinkKeepCurrentBackLink } = useContentLink();
      return { genContentLinkKeepCurrentBackLink };
    },
    props: {
      allowDownloads: {
        type: Boolean,
        default: false,
      },
      topic: {
        type: Object,
        required: true,
      },
      subTopicLoading: {
        type: Boolean,
        default: false,
        required: false,
      },
    },
    data: function () {
      return {
        topicExpanded: false
      }
    },
    computed: {
      topicKnowledgemap() {
        return get(this.$store.state.examViewer.knowledgemap, 'results', []).find(d => d.id === this.topic.id )?.children || [];
      },
      percent() {
        const progress = get(this.$store.state.examViewer.knowledgemap, 'results', []).find(d => d.id === this.topic.id )?.progress_fraction || 0
        return Math.max(Math.min(progress * 100, 100), 0);
      },
    },
    methods: {
      onExpansionClick() {
        this.topicExpanded = !this.topicExpanded
      },
    },
  };

</script>


<style lang="scss" scoped>

  .folder-header-link {
    /deep/ .link-text {
      text-decoration: none !important;
    }
  }

  .more-after-grid {
    margin-bottom: 16px;
  }

  .topic-subsection-wrapper {
    display: flex;
    flex-direction: column;
    border-radius: 8px 8px 8px 8px;
    overflow: hidden;
    margin-bottom: 16px;

    .topic-subsection-header {
      display: flex;
      align-items: center;
      background-color: #061D49;
      border-radius: 8px 8px 0 0;
      padding: 16px;
      cursor: pointer;
      position: relative;
      & h2 {
        margin: 0;
        color: white !important;
      }
      & svg {
        fill: white !important;
        font-size: 2rem;
        top: 0 !important;
        transition: all 0.3s linear;
      }

      & .topic-logo {
        height: 48px;
        width: 48px;
        border-radius: 50%;
        margin-right: 16px;
        object-fit: cover;
      }

      .progress-bar-wrapper {
        position: absolute;
        bottom: 0px;
        left: 0;
        width: 100%;
        height: 5px;
        opacity: 0.9;
        background-color: rgb(224, 224, 224);
      }

      .progress-bar {
        height: 100%;
      }
    }

    .topic-subsection-body {
      display: none;
      background-color: white;
      padding: 30px 60px;
    }

    &.topic-subsection-expanded {
      .topic-subsection-header {
        & svg {
          transform: rotate(180deg);
        }
      }

      .topic-subsection-body {
        display: flex;
        flex-direction: column;
      }
    }
  }

</style>
