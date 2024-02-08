<template>

  <KNavbar>
    <KNavbarLink :title="$tr('channels')" :link="channelsLink">
      <mat-svg name="apps" category="navigation" />
    </KNavbarLink>
    <KNavbarLink
      v-if="isUserLoggedIn && userHasMemberships"
      name="classes-link"
      :title="$tr('classes')"
      :link="allClassesLink"
    >
      <mat-svg
        name="business"
        category="communication"
      />
    </KNavbarLink>
    

  </KNavbar>

</template>


<script>

  import { mapGetters, mapState } from 'vuex';
  import KNavbar from 'kolibri.coreVue.components.KNavbar';
  import KNavbarLink from 'kolibri.coreVue.components.KNavbarLink';
  import { ClassesPageNames, PageNames } from '../constants';

  export default {
    name: 'EdulutionTopNav',
    components: {
      KNavbar,
      KNavbarLink,
    },
    props: {},
    data() {
      return {
        allClassesLink: {
          name: ClassesPageNames.ALL_CLASSES,
        },
        channelsLink: {
          name: PageNames.EDULUTION_TOPICS_ROOT,
        },
        /*recommended link removed*/
      };
    },
    computed: {
      ...mapGetters(['isUserLoggedIn']),
      ...mapState({
        userHasMemberships: state => state.memberships.length > 0,
      }),
    },
    methods: {},
    $trs: {
      /*change text to display channels as Playlists*/
      channels: 'Playlists',
      classes: 'Classes',
    },
  };

</script>


<style lang="scss" scoped></style>
