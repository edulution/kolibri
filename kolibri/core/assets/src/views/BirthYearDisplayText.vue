<template>

  <span v-if="isSpecified && birthYear">
    {{ birthYear }}
  </span>

</template>


<script>

  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import { DemographicConstants } from 'kolibri.coreVue.vuex.constants';

  const { NOT_SPECIFIED, DEFERRED } = DemographicConstants;

  export default {
    name: 'BirthYearDisplayText',
    mixins: [commonCoreStrings],
    props: {
      birthYear: {
        type: String,
      },
    },
    computed: {
      isSpecified() {
        return this.birthYear !== NOT_SPECIFIED && this.birthYear !== DEFERRED;
      },
    },
  };

</script>


<style lang="scss" scoped></style>
