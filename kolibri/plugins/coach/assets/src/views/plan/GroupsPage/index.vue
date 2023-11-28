<template>

  <CoachAppBarPage
    :authorized="userIsAuthorized"
    authorizedRole="adminOrCoach"
    :showSubNav="true"
  >
    <KPageContainer>
      <PlanHeader :activeTabId="PlanTabs.GROUPS" />
      <KTabsPanel
        :tabsId="PLAN_TABS_ID"
        :activeTabId="PlanTabs.GROUPS"
      >
        <div class="ta-r">
          <KButton
            :text="$tr('newGroupAction')"
            :primary="true"
            @click="openCreateGroupModal"
          />
        </div>

        <CoreTable
          :dataLoading="groupsAreLoading"
          :emptyMessage="$tr('noGroups')"
        >
          <template #headers>
            <th>{{ coachString('nameLabel') }}</th>
            <th>{{ coreString('learnersLabel') }}</th>
            <th></th>
          </template>
          <template #tbody>
            <tbody>
              <GroupRowTr
                v-for="group in sortedGroups"
                :key="group.id"
                :group="group"
                @rename="openRenameGroupModal"
                @delete="openDeleteGroupModal"
                @subscribe="openSubscribeGroupModal"
              />
            </tbody>
          </template>
        </CoreTable>

        <CreateGroupModal
          v-if="showCreateGroupModal"
          :groups="sortedGroups"
          @submit="handleSuccessCreateGroup"
          @cancel="closeModal"
        />

        <RenameGroupModal
          v-if="showRenameGroupModal"
          :groupName="selectedGroup.name"
          :groupId="selectedGroup.id"
          :groups="sortedGroups"
          @cancel="closeModal"
        />

        <DeleteGroupModal
          v-if="showDeleteGroupModal"
          :groupName="selectedGroup.name"
          :groupId="selectedGroup.id"
          @submit="handleSuccessDeleteGroup"
          @cancel="closeModal"
        />
      </KTabsPanel>

      <KModal
        v-if="subscriptionModalOpen"
        :title="coreString('channelSubscriptionModalTitle') + subscriptionModalData.groupName"
        :cancelText="coreString('closeAction')"
        :submitText="coreString('saveAction')"
        @cancel="onSubscriptionModalCancel"
        @submit="onSubscriptionModalSubmit"
      >
        <KCheckbox
          v-for="(channel, index) in channels"
          :key="index"
          :label="channel.title"
          :checked="selectedChannelsIds.includes(channel.id)"
          @change="$event => onChannelChange(channel.id)"
        />
        <p>{{ $tr('channelSubscriptionNote') }}</p>
      </KModal>
    </KPageContainer>
  </CoachAppBarPage>

</template>


<script>

  import { ref } from 'kolibri.lib.vueCompositionApi';
  import { mapState, mapActions } from 'vuex';
  import orderBy from 'lodash/orderBy';
  import CoreTable from 'kolibri.coreVue.components.CoreTable';
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import commonCoach from '../../common';
  import { useGroups } from '../../../composables/useGroups';
  import CoachAppBarPage from '../../CoachAppBarPage';
  import PlanHeader from '../../plan/PlanHeader';
  import { GroupModals } from '../../../constants';
  import { PLAN_TABS_ID, PlanTabs } from '../../../constants/tabsConstants';
  import CreateGroupModal from './CreateGroupModal';
  import GroupRowTr from './GroupRow';
  import RenameGroupModal from './RenameGroupModal';
  import DeleteGroupModal from './DeleteGroupModal';

  export default {
    name: 'GroupsPage',
    components: {
      CoachAppBarPage,
      CoreTable,
      PlanHeader,
      GroupRowTr,
      CreateGroupModal,
      RenameGroupModal,
      DeleteGroupModal,
    },
    mixins: [commonCoach, commonCoreStrings],
    setup() {
      const { groupsAreLoading } = useGroups();
      const selectedGroup = ref({
        name: '',
        id: '',
      });

      return {
        PLAN_TABS_ID,
        PlanTabs,
        selectedGroup,
        setSelectedGroup(name, id) {
          selectedGroup.value = { name, id };
        },
        groupsAreLoading,
      };
    },
    data() {
      return {
        subscriptionModalOpen: false,
        subscriptionModalData: {},
        selectedChannelsIds: [],
      }
    },
    computed: {
      ...mapState('groups', ['groupModalShown', 'groups']),
      showCreateGroupModal() {
        return this.groupModalShown === GroupModals.CREATE_GROUP;
      },
      showRenameGroupModal() {
        return this.groupModalShown === GroupModals.RENAME_GROUP;
      },
      showDeleteGroupModal() {
        return this.groupModalShown === GroupModals.DELETE_GROUP;
      },
      sortedGroups() {
        return orderBy(this.groups, [group => group.name.toUpperCase()], ['asc']);
      },
      channels() {
        return this.$store.state.core.channels.list;
      },
    },
    methods: {
      ...mapActions('groups', ['displayModal']),
      ...mapActions('subscriptions', ['saveGroupSubscription']),
      closeModal() {
        this.displayModal(false);
      },
      openCreateGroupModal() {
        this.displayModal(GroupModals.CREATE_GROUP);
      },
      openRenameGroupModal(groupName, groupId) {
        this.setSelectedGroup(groupName, groupId);
        this.displayModal(GroupModals.RENAME_GROUP);
      },
      openDeleteGroupModal(groupName, groupId) {
        this.setSelectedGroup(groupName, groupId);
        this.displayModal(GroupModals.DELETE_GROUP);
      },
      handleSuccessCreateGroup() {
        this.showSnackbarNotification('groupCreated');
        this.displayModal(false);
      },
      handleSuccessDeleteGroup() {
        this.showSnackbarNotification('groupDeleted');
        this.displayModal(false);
      },
      openSubscribeGroupModal(groupName, groupId, subscriptions) {
        this.subscriptionModalOpen = true;
        this.subscriptionModalData = { groupName, groupId };
        this.selectedChannelsIds = subscriptions.length ? JSON.parse(subscriptions) : subscriptions;
      },
      onSubscriptionModalCancel() {
        this.subscriptionModalOpen = false;
        this.subscriptionModalData = {};
        this.selectedChannelsIds = [];
      },
      onSubscriptionModalSubmit() {
        this.saveGroupSubscription({
            id: this.subscriptionModalData.groupId,
            choices: JSON.stringify(this.selectedChannelsIds),
        });

        this.$router.go(this.$router.currentRoute)
        
        this.subscriptionModalOpen = false;
        this.subscriptionModalData = {};
        this.selectedChannelsIds = [];
      },
      onChannelChange(channelId) {
        let selectedChannelsIds = [...this.selectedChannelsIds];
        if (selectedChannelsIds.includes(channelId)) {
          selectedChannelsIds = selectedChannelsIds.filter(d => d !== channelId)
        } else {
          selectedChannelsIds.push(channelId)
        }
        this.selectedChannelsIds = selectedChannelsIds
      }
    },
    $trs: {
      newGroupAction: {
        message: 'New group',
        context:
          "Button used to create a new group of learners. Located on the 'Plan your class' page for coaches.",
      },
      noGroups: {
        message: 'You do not have any groups',
        context: 'Message displayed when there are no groups within a class.',
      },
      channelSubscriptionNote: {
        message: 'Chosen channels will be available in the class',
        context: 'This message displays as helper note inside channel subscription modal',
      },
    },
  };

</script>


<style lang="scss" scoped>

  .ta-r {
    text-align: right;
  }

</style>
