<template>

  <div>
    <KRadioButton
      :value="true"
      :label="$tr('entireClass')"
      :currentValue="entireClassIsSelected"
      :disabled="disabled"
      @change="selectEntireClass()"
    />
    <KCheckbox
      v-for="group in groups"
      :key="group.id"
      :label="group.name"
      :checked="groupIsChecked(group.id)"
      :disabled="disabled"
      @change="toggleGroup($event, group.id)"
    />

    <!-- Individual learners -->
    <IndividualLearnerSelector
      :isVisible="individualSelectorIsVisible"
      :selectedGroupIds="selectedGroupIds"
      :selectedLearnerIds.sync="selectedLearnerIds"
      :targetClassId="classId"
      :disabled="disabled"
      @togglevisibility="toggleIndividualSelector"
    />
  </div>

</template>


<script>

  import isEqual from 'lodash/isEqual';
  import KCheckbox from 'kolibri.coreVue.components.KCheckbox';
  import KRadioButton from 'kolibri.coreVue.components.KRadioButton';
  import { coachStringsMixin } from '../../common/commonCoachStrings';
  import IndividualLearnerSelector from './IndividualLearnerSelector';

  export default {
    name: 'RecipientSelector',
    components: {
      KCheckbox,
      KRadioButton,
      IndividualLearnerSelector,
    },
    mixins: [coachStringsMixin],
    props: {
      // Needs to equal [classId] if entire class is selected
      // Otherwise, [groupId_1, groupId_2] for individual Learner Groups
      value: {
        type: Array,
        required: true,
      },
      // Array of objects, each with 'group' and 'name'
      groups: {
        type: Array,
        required: true,
        validator(value) {
          for (let i = 0; i < value.length; i++) {
            if (!value[i].name || !value[i].id) {
              return false;
            }
          }
          return true;
        },
      },
      // For the 'Entire Class' option
      classId: {
        type: String,
        required: true,
      },
      disabled: {
        type: Boolean,
        default: false,
      },
      initialAdHocLearners: {
        type: Array,
        required: false,
        default: new Array(),
      },
    },
    data() {
      return {
        // Determines whether the individual learner table is visible.
        // Is initially open if item is assigned to individuals.
        individualSelectorIsVisible: this.initialAdHocLearners.length > 0,
        // This is .sync'd with IndividualLearnerSelector, but not with AssignmentDetailsModal
        // which recieves updates via handler in watch.selectedLearnerIds
        selectedLearnerIds: [...this.initialAdHocLearners],
        // Determines whether the group's checkbox is checked and affects which
        // learners are selectable in IndividualLearnerSelector
        selectedGroupIds: this.value.filter(id => id !== this.classId),
      };
    },
    computed: {
      // entireClassIsSelected() {
      //   return isEqual(this.value, [this.classId]) || !this.value.length;
      // },
      entireClassIsSelected() {
        return this.selectedLearnerIds.length === 0 && this.selectedGroupIds.length === 0;
      },
      currentCollectionIds() {
        if (this.entireClassIsSelected) {
          return [this.classId];
        } else {
          return this.selectedGroupIds;
        }
      },
    },
    watch: {
      selectedLearnerIds(newVal) {
        this.$emit('updateLearners', newVal);
      },
      currentCollectionIds(newVal) {
        this.$emit('input', newVal);
      },
    },
    methods: {
      groupIsChecked(groupId) {
        return this.value.includes(groupId);
      },
      selectEntireClass() {
        this.$emit('input', [this.classId]);
      },
      toggleIndividualSelector(isChecked) {
        if (!isChecked) {
          this.clearLearnerIds();
        } else {
          this.individualSelectorIsVisible = true;
        }
      },
      groupIsSelected({ id }) {
        return this.value.includes(id);
      },
      clearLearnerIds() {
        this.selectedLearnerIds = [];
        this.individualSelectorIsVisible = false;
      },
      toggleGroup(isChecked, id) {
        let newValue;
        if (isChecked) {
          // If a group is selected, remove classId if it is there
          newValue = [...this.value].filter(id => id !== this.classId);
          this.$emit('input', [...newValue, id]);
        } else {
          newValue = [...this.value].filter(groupId => id !== groupId);
          // If un-selecting the last group, auto-select 'Entire Class'
          if (newValue.length === 0) {
            newValue = [this.classId];
          }
          this.$emit('input', newValue);
        }
      },
    },
    $trs: {
      entireClass: 'Entire class',
    },
  };

</script>


<style lang="scss" scoped></style>
