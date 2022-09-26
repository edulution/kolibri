<template>

  <div>
    <PageHeader
      :title="$tr('channels')"
      class="visuallyhidden"
    />
    <ContentCardGroupGrid
      v-if="channels.length"
      class="grid"
      :contents="channels"
      :genContentLink="genChannelLink"
    />
  </div>

</template>


<script>

  import { mapState } from 'vuex';
  import { PageNames } from '../constants';
  import PageHeader from '../../../../learn/assets/src/views/PageHeader';
  import ContentCardGroupGrid from './ContentCardGroupGrid';

  export default {
    name: 'ChannelsPage',
    $trs: {
      /*change text from channels to playlists on edulution plugin*/
      /*because coaches and learners already familiar with this term*/
      channels: 'Playlists',
      documentTitle: 'All Playlists',
    },
    metaInfo() {
      return {
        title: this.$tr('documentTitle'),
      };
    },
    components: {
      PageHeader,
      ContentCardGroupGrid,
    },
    computed: {
      ...mapState('topicsRoot', { channels: 'rootNodes' }),
    },
    methods: {
      genChannelLink(channel_id) {
        return {
          name: PageNames.KNOWLEDGE_MAP,
          params: { id: channel_id },
        };
      },
    },
  };

</script>


<style lang="scss" scoped>

  .grid {
    margin-top: 24px;
  }

</style>
