<template>

  <KModal
    :title="$tr('editUserDetailsHeader')"
    :submitText="$tr('save')"
    :cancelText="$tr('cancel')"
    :submitDisabled="isBusy"
    @submit="submitForm"
    @cancel="displayModal(false)"
  >
    <KTextbox
      ref="name"
      v-model="newName"
      type="text"
      :label="$tr('fullName')"
      :autofocus="true"
      :maxlength="120"
      :invalid="nameIsInvalid"
      :invalidText="nameIsInvalidText"
      @blur="nameBlurred = true"
    />

    <KTextbox
      ref="username"
      v-model="newUsername"
      type="text"
      :label="$tr('username')"
      :maxlength="30"
      :invalid="usernameIsInvalid"
      :invalidText="usernameIsInvalidText"
      @blur="usernameBlurred = true"
      @input="setError(null)"
    />

    <template v-if="editingSuperAdmin">
      <h2 class="user-type header">
        {{ $tr('userType') }}
      </h2>

      <UserTypeDisplay
        :userType="kind"
        class="user-type"
      />

      <KExternalLink
        v-if="devicePermissionsPageLink"
        class="super-admin-description"
        :text="editingSelf ? $tr('viewInDeviceTabPrompt') : $tr('changeInDeviceTabPrompt')"
        :href="devicePermissionsPageLink"
      />

    </template>

    <template v-else>
      <KSelect
        v-model="typeSelected"
        :label="$tr('userType')"
        :options="userTypeOptions"
      />

      <fieldset v-if="coachIsSelected" class="coach-selector">
        <KRadioButton
          v-model="classCoachIsSelected"
          :label="$tr('classCoachLabel')"
          :description="$tr('classCoachDescription')"
          :value="true"
        />
        <KRadioButton
          v-model="classCoachIsSelected"
          :label="$tr('facilityCoachLabel')"
          :description="$tr('facilityCoachDescription')"
          :value="false"
        />
        </fieldset>
        </fieldset>
            <fieldset class="soft-delete">
        <legend>{{ $tr('statusLabel') }}</legend>
        <KRadioButton
          v-model="softDeleteValue"
          :label="$tr('changeSoftDeleteStatusActive')"
          :value="false"
        />
        <KRadioButton
          v-model="softDeleteValue"
          :label="$tr('changeSoftDeleteStatusInactive')"
          :value="true"
        />
      </fieldset>
    </template>

    <KTextbox 
      ref="examNumber"
      v-model="newExamNumber"
      type="text"
      :label="$tr('examNumber')"
      :maxlength="20"
      :invalid="examNumberIsInvalid"
      :invalidText="examNumberIsInValidText"
      @blur="examNumberBlurred = true"
      @input="setError(null)"
    />
    <BirthYearSelect
      :value.sync="newBirthYear"
      class="select"
    />

    <GenderSelect
      :value.sync="newGender"
      class="select"
    />
    
  </KModal>

</template>


<script>

  import { mapActions, mapState, mapGetters } from 'vuex';
  import urls from 'kolibri.urls';
  import { UserKinds, ERROR_CONSTANTS } from 'kolibri.coreVue.vuex.constants';
  import { validateUsername } from 'kolibri.utils.validators';
  import KModal from 'kolibri.coreVue.components.KModal';
  import KTextbox from 'kolibri.coreVue.components.KTextbox';
  import KExternalLink from 'kolibri.coreVue.components.KExternalLink';
  import UserTypeDisplay from 'kolibri.coreVue.components.UserTypeDisplay';
  import KSelect from 'kolibri.coreVue.components.KSelect';
  import KRadioButton from 'kolibri.coreVue.components.KRadioButton';
  import GenderSelect from 'kolibri.coreVue.components.GenderSelect';
  import BirthYearSelect from 'kolibri.coreVue.components.BirthYearSelect';

  // IDEA use UserTypeDisplay for strings in options
  export default {
    name: 'EditUserModal',
    $trs: {
      editUserDetailsHeader: 'Edit user details',
      fullName: 'Full name',
      username: 'Username',
      userType: 'User type',
      admin: 'Admin',
      coach: 'Coach',
      learner: 'Learner',
      save: 'Save',
      cancel: 'Cancel',
      required: 'This field is required',
      usernameAlreadyExists: 'Username already exists',
      changeInDeviceTabPrompt: 'Go to Device permissions to change this',
      viewInDeviceTabPrompt: 'View details in Device permissions',
      usernameNotAlphaNumUnderscore: 'Username can only contain letters, numbers, and underscores',
      classCoachLabel: 'Class coach',
      classCoachDescription: "Can only instruct classes that they're assigned to",
      facilityCoachLabel: 'Facility coach',
      facilityCoachDescription: 'Can instruct all classes in your facility',
      examNumber: 'Exam/ID number (Optional)',
      examNumberAlreadyExists: 'Exam number/ID number already exists',
      changeSoftDeleteStatusActive: 'Activate',
      changeSoftDeleteStatusInactive: 'Deactivate',
      statusLabel: 'Status',
    },
    components: {
      KModal,
      KTextbox,
      KSelect,
      KRadioButton,
      KExternalLink,
      UserTypeDisplay,
      GenderSelect,
      BirthYearSelect,
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
      kind: {
        type: String,
        required: true,
      },
      examNumber: {
        type: String,
        required: true,
      },
      gender: {
        type: String,
        required: true,
      },
      birthYear: {
        type: String,
        required: true,
      },
       initialSoftDelete: {
        type: Boolean,
        required: false,
      },
    },
    data() {
      return {
        newName: this.name,
        newUsername: this.username,
        classCoachIsSelected: true,
        typeSelected: null, // see beforeMount
        nameBlurred: false,
        usernameBlurred: false,
        newExamNumber: this.examNumber,
        newBirthYear: this.birthYear,
        newGender: this.gender,
        examNumberBlurred: false,
        softDeleteValue: this.initialSoftDelete,
      };
    },
    computed: {
      ...mapGetters(['currentFacilityId', 'currentUserId']),
      ...mapState('userManagement', ['facilityUsers', 'error', 'isBusy']),
      coachIsSelected() {
        return this.typeSelected.value === UserKinds.COACH;
      },
      userTypeOptions() {
        return [
          {
            label: this.$tr('learner'),
            value: UserKinds.LEARNER,
          },
          {
            label: this.$tr('coach'),
            value: UserKinds.COACH,
          },
          {
            label: this.$tr('admin'),
            value: UserKinds.ADMIN,
          },
        ];
      },
      nameIsInvalidText() {
        if (this.nameBlurred) {
          if (this.newName === '') {
            return this.$tr('required');
          }
        }
        return '';
      },
      nameIsInvalid() {
        return Boolean(this.nameIsInvalidText);
      },
      usernameAlreadyExists() {
        // Just return if it's the same username with a different case
        if (this.username.toLowerCase() === this.newUsername.toLowerCase()) {
          return false;
        }

        if (this.error) {
          if (this.error.includes(ERROR_CONSTANTS.USERNAME_ALREADY_EXISTS)) {
            return true;
          }
        }

        return this.facilityUsers.find(
          ({ username }) => username.toLowerCase() === this.newUsername.toLowerCase()
        );
      },
      usernameIsInvalidText() {
        if (this.usernameBlurred) {
          if (this.newUsername === '') {
            return this.$tr('required');
          }
          if (this.usernameAlreadyExists) {
            return this.$tr('usernameAlreadyExists');
          }
          if (!validateUsername(this.newUsername)) {
            return this.$tr('usernameNotAlphaNumUnderscore');
          }
        }
        return '';
      },
      usernameIsInvalid() {
        return Boolean(this.usernameIsInvalidText);
      },
      examNumberAlreadyExists() {
        if (this.examNumber === this.newExamNumber) {
          return false;
        }

        if (this.error) {
          if (this.error.includes(ERROR_CONSTANTS.EXAM_NUMBER_ALREADY_EXISTS)) {
            return true;
          }
        }
        return this.facilityUsers.find(({ exam_number }) => exam_number === this.newExamNumber);
      },
      examNumberIsInValidText() {
        if (this.examNumberBlurred) {
          if (this.newExamNumber === '') {
            return '';
          }
          if (this.examNumberAlreadyExists) {
            return this.$tr('examNumberAlreadyExists');
          }
        }
        return '';
      },
      examNumberIsInvalid() {
        return Boolean(this.examNumberIsInValidText);
      },
      formIsInvalid() {
        return this.nameIsInvalid || this.usernameIsInvalid || this.examNumberIsInvalid;
      },
      editingSelf() {
        return this.currentUserId === this.id;
      },
      editingSuperAdmin() {
        return this.kind === UserKinds.SUPERUSER;
      },
      devicePermissionsPageLink() {
        const devicePageUrl = urls['kolibri:devicemanagementplugin:device_management'];
        if (devicePageUrl) {
          return `${devicePageUrl()}#/permissions/${this.id}`;
        }
      },
      newType() {
        // never got the chance to even change it
        if (this.editingSuperAdmin) {
          return '';
        }
        if (this.typeSelected.value === UserKinds.COACH) {
          if (this.classCoachIsSelected) {
            return UserKinds.ASSIGNABLE_COACH;
          }

          return UserKinds.COACH;
        }
        return this.typeSelected.value;
      },
    },
    beforeMount() {
      const coachOption = this.userTypeOptions[1];
      if (this.kind === UserKinds.ASSIGNABLE_COACH) {
        this.typeSelected = coachOption;
        this.classCoachIsSelected = true;
      } else if (this.kind === UserKinds.COACH) {
        this.typeSelected = coachOption;
        this.classCoachIsSelected = false;
      } else {
        this.typeSelected = this.userTypeOptions.find(kind => kind.value === this.kind) || {};
      }
    },
    methods: {
      ...mapActions('userManagement', ['updateUser', 'displayModal', 'setError', 'displayModal']),
      ...mapActions(['kolibriLogout']),
      submitForm() {
        if (this.formIsInvalid) {
          if (this.nameIsInvalid) {
            this.$refs.name.focus();
          } else if (this.usernameIsInvalid) {
            this.$refs.username.focus();
          } else if (this.examNumberIsInvalid) {
            this.$refs.examNumber.focus();
          }

          return;
        }

        const updates = {
          username: this.newUsername,
          full_name: this.newName,
          exam_number: this.newExamNumber,
          gender: this.newGender,
          birth_year: this.newBirthYear,
          deleted: this.softDeleteValue,
        };

        if (this.newType) {
          updates.role = {
            collection: this.currentFacilityId,
            kind: this.newType,
          };
        }

        this.updateUser({
          userId: this.id,
          updates,
        }).then(() => {
          // newType is falsey if Super Admin, since that's not a facility role
          if (this.editingSelf && this.newType && this.newType !== UserKinds.ADMIN) {
            // user has demoted themselves
            this.kolibriLogout();
          }
          this.displayModal(false);
        });
      },
    },
  };

</script>


<style lang="scss" scoped>

  .coach-selector {
    padding: 0;
    margin: 0;
    margin-bottom: 3em;
    border: 0;
  }

  .edit-user-form {
    min-height: 350px;
  }

  .super-admin-description,
  .user-type.header,
  .user-admin {
    display: block;
  }

  .super-admin-description {
    font-size: 12px;
  }

  .user-type.header {
    font-size: 16px;
  }
  
  .select {
    margin: 18px 0 36px;
  }

  .soft-delete {
    padding: 0;
    margin: 0;
    border: 0;
  }
  legend {
    padding-top: 16px;
    padding-bottom: 8px;
  }

</style>
