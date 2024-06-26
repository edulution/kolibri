<template>
  <CoreBase :immersivePage="false" :appBarTitle="coachStrings.$tr('coachLabel')" :authorized="userIsAuthorized" authorizedRole="adminOrCoach" :showSubNav="false">
    <TopNavbar slot="sub-nav" />
    <KPageContainer>
      <h1>{{ coachStrings.$tr('classesLabel') }}</h1>
      <p>{{ $tr('classPageSubheader') }}</p>
      <p v-if="classList.length === 0">
        <KExternalLink v-if="isAdmin && createClassUrl" :text="$tr('noClassesDetailsForAdmin')" :href="createClassUrl" />
        <span v-else>
          {{ emptyStateDetails }}
        </span>
      </p>
      <CoreTable v-else>
        <thead slot="thead">
          <tr>
            <th>{{ $tr('classNameLabel') }}</th>
            <th v-if="userIsAdminOrSuperuser">{{ coachStrings.$tr('coachesLabel') }}</th>
            <th>{{ coachStrings.$tr('learnersLabel') }}</th>
            <th v-if="userIsAdminOrSuperuser">{{ $tr('channelsLabel') }}</th>
          </tr>
        </thead>
        <transition-group slot="tbody" tag="tbody" name="list">
          <tr v-for="classObj in classList" :key="classObj.id">
            <td>
              <KLabeledIcon>
                <KIcon slot="icon" classroom />
                <KRouterLink :text="classObj.name" :to="$router.getRoute('HomePage', { classId: classObj.id })" />
              </KLabeledIcon>
            </td>
            <td v-if="userIsAdminOrSuperuser">
              <TruncatedItemList :items="classObj.coaches.map(c => c.full_name)" />
            </td>
            <td>
              {{ coachStrings.$tr('integer', { value: classObj.learner_count }) }}
            </td>
            <td v-if="userIsAdminOrSuperuser">
              <div class="button">
                <KButton :primary="false" :text="$tr('subscribeChannelsButton')" @click="openSubscribeModal(classObj)" />
              </div>
            </td>
          </tr>
        </transition-group>
      </CoreTable>
      <SubscribeModal v-if="subscriptionModalShown===Modals.CHOOSE_CLASS_SUBSCRIPTIONS" :collectionId="currentClass.id" :collectionName="currentClass.name" />
    </KPageContainer>
  </CoreBase>
</template>
<script>

  import { mapGetters, mapState, mapActions } from 'vuex';
  import KExternalLink from 'kolibri.coreVue.components.KExternalLink';
  import urls from 'kolibri.urls';
  import { SubscriptionModals } from '../constants/subscriptionsConstants';
  import commonCoach from './common';
  import SubscribeModal from './SubscribeModal';

  export default {
    name: 'CoachClassListPage',
    components: {
      SubscribeModal,
      KExternalLink,
    },
    mixins: [commonCoach],
    data() {
      return {
        currentClass: null,
      };
    },
    computed: {
      ...mapGetters(['isSuperuser', 'isAdmin', 'isClassCoach', 'isFacilityCoach']),
      ...mapState(['classList']),
      ...mapState('subscriptions', ['subscriptionModalShown', 'selectedSubscriptions']),
      Modals: () => SubscriptionModals,
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
      },
      createClassUrl() {
        const facilityUrl = urls['kolibri:facilitymanagementplugin:facility_management'];
        if (facilityUrl) {
          return facilityUrl();
        }
      },
      userIsAdminOrSuperuser() {
        return this.isAdmin || this.isSuperuser;
      },
    },
    methods: {
      ...mapActions('subscriptions', ['displaySubscriptionModal']),
      openSubscribeModal(classModel) {
        this.currentClass = classModel;
        this.displaySubscriptionModal(SubscriptionModals.CHOOSE_CLASS_SUBSCRIPTIONS);
      },
    },
    $trs: {
      classPageSubheader: 'View learner progress and class performance',
      classNameLabel: 'Class name',
      noAssignedClassesHeader: "You aren't assigned to any classes",
      noAssignedClassesDetails:
        'Please consult your Kolibri administrator to be assigned to a class',
      noClassesDetailsForAdmin: 'Create a class and enroll learners',
      noClassesDetailsForFacilityCoach: 'Please consult your Kolibri administrator',
      noClassesInFacility: 'There are no classes yet',
      subscribeChannelsButton: 'SUBSCRIBE CHANNELS',
      channelsLabel: 'Channels',
    },
  };

</script>
<style lang="scss" scoped></style>
