<template>

  <KModal
    :title="$tr('prerequisitesText')"
    :submitText="$tr('close')"
    :cancelText="$tr('goToLesson')"
    :cancelDisabled="isLearner"
    @submit="close"
    @cancel="goToLesson"
  >
    <section>
      <ul>
        <li v-for="prerequisite in prerequisites" class="list-link">
          <KRouterLink
            :text="prerequisite.title"
            :to="genLink(prerequisite.id)"
            dir="auto"
            @click.native="close()"
          />
          {{ '(' + Math.round(prerequisite.progress * 100) + '%)' }}
        </li>
      </ul>

    </section>

  </KModal>

</template>


<script>

  import { mapGetters, mapState } from 'vuex';
  import KModal from 'kolibri.coreVue.components.KModal';
  /*import { validateLinkObject } from 'kolibri.utils.validators';*/
  import KRouterLink from 'kolibri.coreVue.components.KRouterLink';
  import { PageNames } from '../constants';

  export default {
    name: 'PrerequisitesModal',
    $trs: {
      prerequisitesText: 'Hi, It looks like you need to complete these actvities first',
      close: 'Go back',
      goToLesson: 'Skip ahead',
    },
    components: {
      KModal,
      KRouterLink,
    },
    computed: {
      ...mapGetters(['isLearner']),
      ...mapState('topicsTree', ['modalShown', 'link', 'prerequisites']),
    },
    methods: {
      close() {
        this.$store.commit('topicsTree/SET_PREREQUISITES_MODAL', false);
        this.$store.commit('topicsTree/SET_PREREQUISITES');
      },
      goToLesson() {
        this.$store.commit('topicsTree/SET_PREREQUISITES_MODAL', false);
        this.$router.push(this.link);
      },
      genLink(id) {
        return {
          name: PageNames.TOPICS_CONTENT,
          params: { id },
        };
      },
    },
  };

</script>


<style lang="scss" scoped>

  .list-link {
    font-weight: bold;
    line-height: 32px;
  }

</style>
