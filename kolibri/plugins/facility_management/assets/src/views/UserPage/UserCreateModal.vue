<template>

  <KModal
    :title="$tr('createNewUserHeader')"
    :submitText="$tr('saveUserButtonLabel')"
    :cancelText="$tr('cancel')"
    :submitDisabled="submitting"
    @submit="createNewUser"
    @cancel="close"
  >
    <section>
      <KTextbox
        ref="name"
        v-model.trim="fullName"
        type="text"
        :label="$tr('name')"
        :autofocus="true"
        :maxlength="120"
        :invalid="nameIsInvalid"
        :invalidText="nameIsInvalidText"
        @blur="nameBlurred = true"
      />
      <KTextbox
        ref="username"
        v-model="username"
        type="text"
        :label="$tr('username')"
        :maxlength="30"
        :invalid="usernameIsInvalid"
        :invalidText="usernameIsInvalidText"
        @blur="usernameBlurred = true"
      />
      <KTextbox
        ref="password"
        v-model="password"
        type="password"
        :label="$tr('password')"
        :invalid="passwordIsInvalid"
        :invalidText="passwordIsInvalidText"
        @blur="passwordBlurred = true"
      />
      <KTextbox
        ref="confirmedPassword"
        v-model="confirmedPassword"
        type="password"
        :label="$tr('reEnterPassword')"
        :invalid="confirmedPasswordIsInvalid"
        :invalidText="confirmedPasswordIsInvalidText"
        @blur="confirmedPasswordBlurred = true"
      />

      <KSelect
        v-model="kind"
        :label="$tr('userType')"
        :options="userKindDropdownOptions"
      />

      <fieldset v-if="coachIsSelected" class="coach-selector">
        <KRadioButton
          v-model="classCoach"
          :label="$tr('classCoachLabel')"
          :description="$tr('classCoachDescription')"
          :value="true"
        />
        <KRadioButton
          v-model="classCoach"
          :label="$tr('facilityCoachLabel')"
          :description="$tr('facilityCoachDescription')"
          :value="false"
        />
      </fieldset>
      <KTextbox 
        ref="examNumber"
        v-model="examNumber"
        type="text"
        :label="$tr('examNumber')"
        :maxlength="20"
        :invalid="examNumberIsInvalid"
        :invalidText="examNumberIsInValidText"
        @blur="examNumberBlurred=true"
      />
      <BirthYearSelect
        class="select"
        :value.sync="birthYear"
      />
      <GenderSelect
        class="select" 
        :value.sync="gender"
      />
      
    </section>
  </KModal>

</template>


<script>

  import { mapActions, mapState, mapGetters } from 'vuex';
  import { UserKinds, ERROR_CONSTANTS } from 'kolibri.coreVue.vuex.constants';
  import { validateUsername } from 'kolibri.utils.validators';
  import CatchErrors from 'kolibri.utils.CatchErrors';
  import KRadioButton from 'kolibri.coreVue.components.KRadioButton';
  import KModal from 'kolibri.coreVue.components.KModal';
  import KTextbox from 'kolibri.coreVue.components.KTextbox';
  import KSelect from 'kolibri.coreVue.components.KSelect';
  import GenderSelect from 'kolibri.coreVue.components.GenderSelect';
  import BirthYearSelect from 'kolibri.coreVue.components.BirthYearSelect';

  export default {
    name: 'UserCreateModal',
    $trs: {
      createNewUserHeader: 'Create new user',
      cancel: 'Cancel',
      name: 'Full name',
      username: 'Username',
      password: 'Password',
      reEnterPassword: 'Re-enter password',
      userType: 'User type',
      saveUserButtonLabel: 'Save',
      learner: 'Learner',
      coach: 'Coach',
      admin: 'Admin',
      coachSelectorHeader: 'Coach type',
      classCoachLabel: 'Class coach',
      classCoachDescription: "Can only instruct classes that they're assigned to",
      facilityCoachLabel: 'Facility coach',
      facilityCoachDescription: 'Can instruct all classes in your facility',
      usernameAlreadyExists: 'Username already exists',
      usernameNotAlphaNumUnderscore: 'Username can only contain letters, numbers, and underscores',
      pwMismatchError: 'Passwords do not match',
      unknownError: 'Whoops, something went wrong. Try again',
      loadingConfirmation: 'Loading...',
      required: 'This field is required',
      examNumber: 'Exam number/ID number (Optional)',
      examNumberAlreadyExists: 'Exam/ID number already exists',
    },
    components: {
      KRadioButton,
      KModal,
      KTextbox,
      KSelect,
      GenderSelect,
      BirthYearSelect,
    },
    data() {
      return {
        fullName: '',
        username: '',
        password: '',
        confirmedPassword: '',
        gender: '',
        birthYear: '',
        examNumber: '',
        kind: {
          label: this.$tr('learner'),
          value: UserKinds.LEARNER,
        },
        classCoach: true,
        usernameAlreadyExistsOnServer: false,
        submitting: false,
        nameBlurred: false,
        usernameBlurred: false,
        passwordBlurred: false,
        confirmedPasswordBlurred: false,
        formSubmitted: false,
        examNumberBlurred: false,
        examNumberAlreadyExistsOnServer: false,
      };
    },
    computed: {
      ...mapGetters(['currentFacilityId']),
      ...mapState('userManagement', ['facilityUsers']),
      newUserRole() {
        if (this.coachIsSelected) {
          if (this.classCoach) {
            return UserKinds.ASSIGNABLE_COACH;
          }
          return UserKinds.COACH;
        }
        // Admin or Learner
        return this.kind.value;
      },
      coachIsSelected() {
        return this.kind.value === UserKinds.COACH;
      },
      nameIsInvalidText() {
        if (this.nameBlurred || this.formSubmitted) {
          if (this.fullName === '') {
            return this.$tr('required');
          }
        }
        return '';
      },
      nameIsInvalid() {
        return Boolean(this.nameIsInvalidText);
      },
      usernameAlreadyExists() {
        return this.facilityUsers.find(
          ({ username }) => username.toLowerCase() === this.username.toLowerCase()
        );
      },
      examNumberAlreadyExists() {
        return this.facilityUsers.find(({ exam_number }) => exam_number === this.examNumber);
      },
      examNumberIsInValidText() {
        if (this.examNumberBlurred || this.formSubmitted) {
          if (this.examNumber === '') {
            return '';
          }
          if (this.examNumberAlreadyExists || this.examNumberAlreadyExistsError) {
            return this.$tr('examNumberAlreadyExists');
          }
        }
        return '';
      },
      examNumberIsInvalid() {
        return Boolean(this.examNumberIsInValidText);
      },
      usernameIsInvalidText() {
        if (this.usernameBlurred || this.formSubmitted) {
          if (this.username === '') {
            return this.$tr('required');
          }
          if (!validateUsername(this.username)) {
            return this.$tr('usernameNotAlphaNumUnderscore');
          }
          if (this.usernameAlreadyExists || this.usernameAlreadyExistsError) {
            return this.$tr('usernameAlreadyExists');
          }
        }
        return '';
      },
      usernameIsInvalid() {
        return Boolean(this.usernameIsInvalidText);
      },
      passwordIsInvalidText() {
        if (this.passwordBlurred || this.formSubmitted) {
          if (this.password === '') {
            return this.$tr('required');
          }
        }
        return '';
      },
      passwordIsInvalid() {
        return Boolean(this.passwordIsInvalidText);
      },
      confirmedPasswordIsInvalidText() {
        if (this.confirmedPasswordBlurred || this.formSubmitted) {
          if (this.confirmedPassword === '') {
            return this.$tr('required');
          }
          if (this.confirmedPassword !== this.password) {
            return this.$tr('pwMismatchError');
          }
        }
        return '';
      },
      confirmedPasswordIsInvalid() {
        return Boolean(this.confirmedPasswordIsInvalidText);
      },
      formIsValid() {
        return (
          !this.nameIsInvalid &&
          !this.usernameIsInvalid &&
          !this.passwordIsInvalid &&
          !this.confirmedPasswordIsInvalid &&
          !this.examNumberIsInvalid
        );
      },
      userKindDropdownOptions() {
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
    },
    methods: {
      ...mapActions('userManagement', ['createUser', 'displayModal']),
      ...mapActions(['handleApiError']),
      createNewUser() {
        this.usernameAlreadyExistsOnServer = false;
        this.examNumberAlreadyExistsOnServer = false;
        this.formSubmitted = true;
        if (this.formIsValid) {
          this.submitting = true;
          this.createUser({
            username: this.username,
            full_name: this.fullName,
            exam_number: this.examNumber,
            gender: this.gender,
            birth_year: this.birthYear,
            role: {
              kind: this.newUserRole,
              collection: this.currentFacilityId,
            },
            password: this.password,
          }).then(
            () => {
              this.close();
            },
            error => {
              const usernameAlreadyExistsError = CatchErrors(error, [
                ERROR_CONSTANTS.USERNAME_ALREADY_EXISTS,
              ]);

              const examNumberAlreadyExistsError = CatchErrors(error, [
                ERROR_CONSTANTS.EXAM_NUMBER_ALREADY_EXISTS,
              ]);
              if (usernameAlreadyExistsError) {
                this.submitting = false;
                this.usernameAlreadyExistsOnServer = true;
              } else if (examNumberAlreadyExistsError) {
                this.submitting = false;
                this.examNumberAlreadyExistsOnServer = true;
              } else {
                this.handleApiError(error);
              }
            }
          );
        } else {
          this.focusOnInvalidField();
        }
      },
      focusOnInvalidField() {
        if (this.nameIsInvalid) {
          this.$refs.name.focus();
        } else if (this.usernameIsInvalid) {
          this.$refs.username.focus();
        } else if (this.passwordIsInvalid) {
          this.$refs.password.focus();
        } else if (this.confirmedPasswordIsInvalid) {
          this.$refs.confirmedPassword.focus();
        } else if (this.examNumberIsInvalid) {
          this.$refs.examNumber.focus();
        }
      },
      close() {
        this.displayModal(false);
      },
    },
  };

</script>


<style lang="scss" scoped>

  .user-create-form {
    min-height: 500px;
  }

  .coach-selector {
    padding: 0;
    margin: 0;
    margin-bottom: 3em;
    border: 0;
  }

</style>
