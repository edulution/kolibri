<template>

  <CoachAppBarPage
    :appBarTitle="appBarTitle"
    :authorized="userIsAuthorized"
    authorizedRole="adminOrCoach"
  >
    <KPageContainer>
      <p>
        <KRouterLink
          v-if="userIsMultiFacilityAdmin"
          :to="{ name: 'AllFacilitiesPage' }"
          :text="coreString('changeLearningFacility')"
          icon="back"
        />
      </p>
      <h1>{{ coreString('classesLabel') }}</h1>
      <p>{{ $tr('classPageSubheader') }}</p>

      <p v-if="classList.length === 0 && !dataLoading">
        <KExternalLink
          v-if="isAdmin && createClassUrl"
          :text="$tr('noClassesDetailsForAdmin')"
          :href="createClassUrl"
        />
      </p>

      <CoreTable v-else :dataLoading="dataLoading" :emptyMessage="emptyStateDetails">
        <template #headers>
          <th>{{ coreString('classNameLabel') }}</th>
          <th>{{ coreString('coachesLabel') }}</th>
          <th>{{ coreString('learnersLabel') }}</th>
          <th>{{ coreString('channelsLabel') }}</th>
        </template>
        <template #tbody>
          <transition-group
            tag="tbody"
            name="list"
          >
            <tr
              v-for="classObj in classList"
              :key="classObj.id"
            >
              <td>
                <KRouterLink
                  :text="classObj.name"
                  :to="$router.getRoute('HomePage', { classId: classObj.id })"
                  icon="classes"
                />
              </td>
              <td>
                <TruncatedItemList :items="classObj.coaches.map(c => c.full_name)" />
              </td>
              <td>
                {{ $formatNumber(classObj.learner_count) }}
              </td>
              <td>
                <KButton
                  :text="coreString('subscribeChannel')"
                  @click="onSubscriptionModalOpen(classObj)"
                />
              </td>
            </tr>
          </transition-group>
        </template>
      </CoreTable>
      <KModal
        v-if="subscriptionModalOpen"
        :title="coreString('channelSubscriptionModalTitle') + subscriptionModalData.name"
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
  import { mapGetters, mapState, mapActions } from 'vuex';
  import find from 'lodash/find';
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import urls from 'kolibri.urls';
  import CoachAppBarPage from './CoachAppBarPage';
  import commonCoach from './common';

  export default {
    name: 'CoachClassListPage',
    components: {
      CoachAppBarPage,
    },
    mixins: [commonCoach, commonCoreStrings],
    data() {
      return {
        subscriptionModalOpen: false,
        subscriptionModalData: {},
        selectedChannelsIds: [],
      }
    },
    computed: {
      ...mapGetters(['isAdmin', 'isClassCoach', 'isFacilityCoach', 'userIsMultiFacilityAdmin']),
      ...mapState(['classList', 'dataLoading']),
      // Message that shows up when state.classList is empty
      emptyStateDetails() {
        if (this.isClassCoach) {
          return this.$tr('noAssignedClassesDetails');
        }
        if (this.isAdmin) {
          return this.$tr('noClassesDetailsForAdmin');
        }
        if (this.isFacilityCoach) {
          return this.$tr('noClassesDetailsForFacilityCoach');
        }

        return '';
      },
      createClassUrl() {
        const facilityUrl = urls['kolibri:kolibri.plugins.facility:facility_management'];
        if (facilityUrl) {
          if (this.userIsMultiFacilityAdmin) {
            return `${facilityUrl()}#/${this.$route.query.facility_id}/classes`;
          }
          return facilityUrl();
        }

        return '';
      },
      appBarTitle() {
        let facilityName;
        const { facility_id } = this.$route.query;
        if (facility_id) {
          const match = find(this.$store.state.core.facilities, { id: facility_id }) || {};
          facilityName = match.name;
        }
        if (facilityName) {
          return this.coachString('coachLabelWithOneName', { name: facilityName });
        } else {
          return this.coachString('coachLabel');
        }
      },
      channels() {
        return this.$store.state.core.channels.list;
      },
    },
    methods: {
      ...mapActions('subscriptions', [
        'saveSubscription',
        'updateGroupSubscriptions',
      ]),
      onSubscriptionModalSubmit() {
        this.updateGroupSubscriptions(this.selectedChannelsIds)
        
        this.saveSubscription({
          id: this.subscriptionModalData.id,
          choices: JSON.stringify(this.selectedChannelsIds)
        })

        this.$router.go(this.$router.currentRoute)
        
        this.subscriptionModalOpen = false;
        this.subscriptionModalData = {};
        this.selectedChannelsIds = [];
      },
      onSubscriptionModalCancel() {
        this.subscriptionModalOpen = false;
        this.subscriptionModalData = {};
        this.selectedChannelsIds = [];
      },
      onSubscriptionModalOpen(classObj) {
        this.subscriptionModalOpen = true;
        this.subscriptionModalData = classObj;
        this.selectedChannelsIds = classObj.subscriptions.length ? JSON.parse(classObj.subscriptions) : classObj.subscriptions;
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
      classPageSubheader: {
        message: 'View learner progress and class performance',
        context:
          'Subtitle of the Coach > Classes section which describes what the coach can see in this section.',
      },
      noAssignedClassesDetails: {
        message: 'Please consult your Kolibri administrator to be assigned to a class',
        context:
          'Coach accounts in Kolibri are created by admins. If the coach has no classes assigned to them by the admin, this message displays in the Coach > Classes section. ',
      },
      noClassesDetailsForAdmin: {
        message: 'Create a class and enroll learners',
        context:
          "This message displays if there are no classes in the 'Classes' section. Admins can create classes and enroll learners to them. ",
      },
      noClassesDetailsForFacilityCoach: {
        message: 'Please consult your Kolibri administrator',
        context:
          'If the coach has no classes assigned to them by the admin, or if they are not themselves an admin themselves, this message displays in the Coach > Classes section.',
      },
      channelSubscriptionNote: {
        message: 'Chosen channels will be available in the class',
        context: 'This message displays as helper note inside channel subscription modal',
      },
    },
  };

</script>


<style lang="scss" scoped>
.subscribe-btn {
    padding: 0 16px;
    font-size: 14px;
    font-weight: 700;
    line-height: 36px;
    border: 0;
    border-radius: 2px;
    background-color: rgb(238, 238, 238);
    -webkit-box-shadow: 0 1px 5px rgba(0,0,0,.2), 0 2px 2px rgba(0,0,0,.14), 0 3px 1px -2px rgba(0,0,0,.12);
    box-shadow: 0 1px 5px rgba(0,0,0,.2), 0 2px 2px rgba(0,0,0,.14), 0 3px 1px -2px rgba(0,0,0,.12);
    color: rgb(33, 33, 33);
    cursor: pointer;
    text-transform: uppercase;
    -webkit-transition: background-color .25s ease;
    transition: background-color .25s ease;
    &:hover {
      background-color: rgb(238, 238, 238);
    }
  }
  </style>
