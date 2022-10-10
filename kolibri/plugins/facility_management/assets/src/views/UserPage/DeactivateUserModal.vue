<template>

  <KModal
    :title="$tr('deactivateUser')"
    :submitText="$tr('deactivate')"
    :cancelText="$tr('cancel')"
    :submitDisabled="submitting"
    @submit="handleDeactivateUser"
    @cancel="closeModal"
  >
    <p>{{ $tr('confirmation', { username: username }) }}</p>
    <!-- <p>{{ $tr('warning', { username: username }) }}</p> -->
  </KModal>

</template>


<script>

  import { mapActions } from 'vuex';
  import KModal from 'kolibri.coreVue.components.KModal';

  export default {
    name: 'DeactivateUserModal',
    $trs: {
      deactivateUser: 'Deactivate user',
      confirmation: "Are you sure you want to deactivate the user '{ username }'?",
      cancel: 'Cancel',
      deactivate: 'Deactivate',
    },
    components: {
      KModal,
    },
    props: {
      id: {
        type: String,
        required: true,
      },
      name: {
        type: String,
        required: true,
      },
      username: {
        type: String,
        required: true,
      },
    },
    data() {
      return {
        submitting: false,
      };
    },
    methods: {
      ...mapActions('userManagement', ['deactivateUser', 'displayModal']),
      handleDeactivateUser() {
        this.submitting = true;
        this.deactivateUser(this.id);
      },
      closeModal() {
        this.displayModal(false);
      },
    },
  };

</script>


<style lang="scss" scoped></style>