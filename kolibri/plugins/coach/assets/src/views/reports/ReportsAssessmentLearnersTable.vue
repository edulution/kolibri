<template>

  <CoreTable :emptyMessage="coachString('learnerListEmptyState')">
    <template #headers>
      <th>{{ coachString('topicLabel') }}</th>
      <th v-if="anyScore">
        {{ coreString('scoreLabel') }}
      </th>
    </template>
    <template #tbody>
      <transition-group tag="tbody" name="list">
        <tr v-for="tableRow in entries" :key="tableRow.id" data-test="entry">
          <td 
            :style="{ backgroundColor: 
              scoreBackgroundColor((tableRow.statusObj.num_correct / questionCount * 100) || 0) }" 
          >
            <template>
              {{ tableRow.name }}
            </template>
          </td>
          <td v-if="anyScore">
            <Score
              v-if="tableRow.statusObj.status === STATUSES.completed"
              :value="tableRow.statusObj.num_correct / questionCount || 0.0"
              :diff="getDiff(tableRow)"
            />
          </td>
        </tr>
      </transition-group>
    </template>
  </CoreTable>
  
</template>
  
  
  <script>
  
    import isUndefined from 'lodash/isUndefined';
    import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
    import commonCoach from '../common';
  
    export default {
      name: 'ReportsAssessmentLearnersTable',
      mixins: [commonCoach, commonCoreStrings],
      props: {
        entries: {
          type: Array,
          default: () => [],
        },
        questionCount: {
          type: Number,
          default: 0,
        },
      },
      computed: {
        anyScore() {
          return (
            this.questionCount &&
            this.entries.some(entry => !isUndefined(entry.statusObj.num_correct))
          );
        },
      },
      methods: {
        getDiff(entry) {
          if (entry.statusObj.status === this.STATUSES.completed && entry.statusObj.tries > 1) {
            return (
              (entry.statusObj.num_correct - entry.statusObj.previous_num_correct) /
              this.questionCount
            );
          }
  
          return null;
        },
        scoreBackgroundColor(value) {
        if (value >= 0 && value < 30) {
          return 'red';
        } else if (value >= 30 && value < 50) {
          return 'blue';
        } else if (value >= 50 && value < 70) {
          return 'black';
        } else if (value >= 70 && value <= 100) {
          return 'pink';
        }
      },
      },
      $trs: {
      },
    };
  
  </script>
  
  
  <style lang="scss" scoped>
  
    @import '../common/print-table';
  
    .small-answered-count {
      display: block;
      margin-left: 1.75rem; /* matches KLabeledIcon */
      font-size: small;
    }
  
  </style>
  