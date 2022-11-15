<template>
  <span>{{ displayText }}</span>
</template>
<script>
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import { FacilityUserSoftDeleted } from 'kolibri.coreVue.vuex.constants';
  const { TRUE, FALSE } = FacilityUserSoftDeleted;
  export default {
    name: 'SoftDeletedDisplayText',
    mixins: [commonCoreStrings],
    props: {
      deleted: {
        type: Boolean,
      },
    },
    computed: {
      displayText() {
        if (this.deleted === TRUE) {
          return this.coreString('deletedOptionDeactivated');
        } else if (this.deleted === FALSE) {
          return this.coreString('deletedOptionActive');
        }
        return null;
      },
    },
  };
</script>
<style lang="scss" scoped></style> 