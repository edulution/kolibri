<template>
  <div>
    <div style="padding-left: 16px; margin: 32px 0 8px 0">
      <h1 class="page-header">
        {{ topic.title }}
      </h1>
      <TextTruncator 
        v-if="topic.description" 
        :text="topic.description" 
        :maxHeight="90" 
        :showTooltip="false" 
        :showViewMore="true" 
        dir="auto" 
        class="page-description"
      />
    </div>
    <div v-if="contents[0].children.length">
      <ExpandableContentCardGroupGrid v-for="child in contents" :key="child.id" :child="child" />
    </div>
    <ContentCardGroupGrid 
      v-if="!contents[0].children.length" 
      :contents="contents" 
      :genContentLink="genContentLink" 
      style="padding-left: 16px; 
      padding-top: 16px"
    />
    <PrerequisitesModal v-if="modalShown" />
  </div>
</template>
<script>

  import { mapGetters, mapState } from 'vuex';
  import { ContentNodeKinds } from 'kolibri.coreVue.vuex.constants';
  import TextTruncator from 'kolibri.coreVue.components.TextTruncator';
  import ProgressIcon from 'kolibri.coreVue.components.ProgressIcon';
  import { PageNames } from '../constants';
  import ContentCardGroupGrid from './ContentCardGroupGrid';
  import ExpandableContentCardGroupGrid from './ExpandableContentCardGroupGrid';
  import PrerequisitesModal from './PrerequisitesModal';

  export default {
    name: 'KnowledgeMap',
    $trs: {
      topics: 'Topics',
      navigate: 'Navigate content using headings',
      documentTitleForChannel: 'Topics - { channelTitle }',
      documentTitleForTopic: '{ topicTitle } - { channelTitle }',
    },
    components: {
      ExpandableContentCardGroupGrid,
      ContentCardGroupGrid,
      TextTruncator,
      ProgressIcon,
      PrerequisitesModal,
    },
    metaInfo() {
      let title;
      if (this.isRoot) {
        title = this.$tr('documentTitleForChannel', {
          channelTitle: this.channelTitle,
        });
      } else {
        title = this.$tr('documentTitleForTopic', {
          channelTitle: this.channelTitle,
          topicTitle: this.topic.title,
        });
      }
      return { title };
    },
    data: function() {
      return {
        hidden: false,
      };
    },
    computed: {
      ...mapGetters(['isLearner']),
      ...mapState('topicsTree', [
        'channel',
        'contents',
        'isRoot',
        'topic',
        'progress',
        'modalShown',
      ]),
      channelId() {
        return this.channel.id;
      },
      channelTitle() {
        return this.channel.title;
      },
    },
    methods: {
      genContentLink(id, kind) {
        if (kind === ContentNodeKinds.TOPIC) {
          return {
            name: PageNames.KNOWLEDGE_MAP,
            params: { channel_id: this.channelId, id },
          };
        }
        return {
          name: PageNames.TOPICS_CONTENT,
          params: { channel_id: this.channelId, id },
        };
      },
    },
  };

</script>
<style lang="scss" scoped>
.page-header {
  margin: 0;
  font-size: 40px;
}

.page-description {
  margin-top: 1em;
  margin-bottom: 1em;
  line-height: 1.5em;
}

</style>
