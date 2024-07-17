/**
 * A composable function containing logic related to channels
 */
import pickBy from 'lodash/pickBy';
import { ref, reactive } from 'kolibri.lib.vueCompositionApi';
import { ChannelResource } from 'kolibri.resources';
import { get, set } from '@vueuse/core';
import { LearnerClassroomResource } from '../apiResources';
import { ClassroomResource, LearnerGroupResource } from '../../../../../core/assets/src/api-resources';

// The refs are defined in the outer scope so they can be used as a shared store
const channelsMap = reactive({});

const localChannelsCache = ref([]);

function fetchChannels(params) {
  params = pickBy(params || {});
  return ChannelResource.list({ available: true, ...params }).then(channels => {
    for (const channel of channels) {
      set(channelsMap, channel.id, channel);
    }
    if (Object.keys(params).length === 0) {
      set(localChannelsCache, channels);
    }
    return channels;
  });
}

function getChannelThumbnail(channelId) {
  const channel = get(channelsMap)[channelId];
  if (channel) {
    return channel.thumbnail;
  }
  return '';
}

function getChannelTitle(channelId) {
  const channel = get(channelsMap)[channelId];
  if (channel) {
    return channel.name;
  }
  return '';
}

async function fetchLearnerChannels({ isLearner, userId }) {
  const channels = await ChannelResource.list();
  let subscribedChannelIds = []
  
  if (isLearner) {
    const learnerGroups = await LearnerGroupResource.fetchCollection();
    const learnerClassrooms = await LearnerClassroomResource.fetchCollection();
    
    for (const group of learnerGroups) {
      if (group.user_ids.includes(userId)) {
        subscribedChannelIds = [
          ...subscribedChannelIds,
          ...(JSON.parse(group.subscriptions || []))
        ];
      }
    }

    for(const learnerClassroom of learnerClassrooms) {
      try {
        const classroom = await ClassroomResource.fetchModel({ id: learnerClassroom.id });  
        if (classroom && classroom.subscriptions) {
          subscribedChannelIds = [
            ...subscribedChannelIds,
            ...(JSON.parse(classroom.subscriptions || []))
          ];
        }
      } catch (error) {
        console.log("error", error)
      }
    }

    return channels.filter(c => subscribedChannelIds.includes(c.id));
  }
  
  return channels
}

export default function useChannels() {
  return {
    channelsMap,
    localChannelsCache,
    fetchChannels,
    getChannelThumbnail,
    getChannelTitle,
    fetchLearnerChannels,
  };
}
