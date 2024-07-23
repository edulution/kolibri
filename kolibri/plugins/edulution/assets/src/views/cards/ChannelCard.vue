<template>
  <div
    v-if="channel"
    class="channel-card"
    :class="{ 'channel-card-fullwidth': fullwidth, 'channel-card-topic': variant === 'topic' }"
  >
    <div>
      <ToggleRouterLink :link="to" :pendingPrerequisites="pendingPrerequisites">
        <ChannelThumbnailNew
          v-if="channel.thumbnail"
          :thumbnail="channel.thumbnail"
          :progress="progress"
          :fullwidth="fullwidth"
          :channel="channel"        
        />

        <div class="text">
          <h3 class="title">
            <TextTruncatorCss dir="auto" :text="channel.title || channel.name" :maxLines="1" />
          </h3>
        </div>
      </ToggleRouterLink>
    </div>
  </div>
</template>

<script>

import TextTruncatorCss from 'kolibri.coreVue.components.TextTruncatorCss';
import ChannelThumbnailNew from '../ChannelThumbnailNew';
import ToggleRouterLink from '../ToggleRouterLink';
import useContentNodeProgress from '../../composables/useContentNodeProgress';

export default {
  name: 'ChannelCard',
  components: {
    ChannelThumbnailNew,
    TextTruncatorCss,
    ToggleRouterLink,
  },
  setup() {
      const { contentNodeProgressMap } = useContentNodeProgress();
      return { contentNodeProgressMap };
    },
  props: {
    channel: {
      type: Object,
      required: true,
    },
    knowledgemap: {
      type: Object,
      required: false,
    },
    to: {
      type: Object,
      required: true,
    },
    fullwidth: {
      type: Boolean,
      required: false,
      default: false,
    },
    variant: {
      type: String,
      required: false,
      default: '',
    },
    pendingPrerequisites: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  computed: {
      progress() {
        if (this.knowledgemap?.progress_fraction) {
          return this.knowledgemap.progress_fraction || 0;
        }
        return this.contentNodeProgressMap[this.channel && this.channel.content_id] || 0;
      },
    },

}
</script>

<style lang="scss" scoped>
.channel-card {
  display: inline-block;
  width: 210px;
  text-decoration: none;
  word-break: break-all;
  word-break: break-word;
  vertical-align: top;
  border-radius: 2px;
  margin-right: 50px;
  margin-bottom: 50px;
  -webkit-box-shadow: 0 1px 3px 0 rgba(0, 0, 0, .2), 0 1px 1px 0 rgba(0, 0, 0, .14), 0 2px 1px -1px rgba(0, 0, 0, .12);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, .2), 0 1px 1px 0 rgba(0, 0, 0, .14), 0 2px 1px -1px rgba(0, 0, 0, .12);
  transition: box-shadow .25s ease;
  transition: box-shadow .25s ease, -webkit-box-shadow .25s ease;

  &:focus {
    outline-width: 4px;
    outline-offset: 6px
  }

  &:hover {
    -webkit-box-shadow: 0 5px 5px -3px rgba(0, 0, 0, .2), 0 8px 10px 1px rgba(0, 0, 0, .14), 0 3px 14px 2px rgba(0, 0, 0, .12);
    box-shadow: 0 5px 5px -3px rgba(0, 0, 0, .2), 0 8px 10px 1px rgba(0, 0, 0, .14), 0 3px 14px 2px rgba(0, 0, 0, .12);
  }


  & .text {
    color: rgb(58, 58, 58);
    position: relative;
    height: 92px;
    padding: 16px;
  }
  & .title {
    margin: 0;
  }

  &.channel-card-fullwidth {
    margin-right: 0 !important;
    width: 100% !important;
  }

  &.channel-card-topic {
    width: calc(33.33% - 60px) !important;
    margin-right: 50px !important;
    margin-bottom: 50px !important;
  }
}

</style>