<template>
  <div>
    <div class="back-row" @click.prevent="$emit('backClick')">
      <KIcon
        icon="back"
      />
      <span>Back to test list</span>
    </div>
  
    <CoreTable :emptyMessage="$tr('emptyMessage')">
      <template #headers>
        <th>{{ coachString('topicLabel') }}</th>
        <th style="width: 120px">
          {{ $tr('scoreLabel') }}
        </th>
      </template>
      <template #tbody>
        <transition-group tag="tbody" name="list">
          <tr v-for="(tableRow, index) in entries" :key="tableRow.id">
            <td>
              {{ tableRow.title }}
            </td>
            <td>
              <span
                class="score-chip"
                :style="{
                  backgroundColor: scoreColor(
                    calcPercentage(tableRow.score, tableRow.question_count)
                  ),
                  color: 'white',
                }"
              >
                {{
                  $formatNumber(
                    calcPercentage(tableRow.score, tableRow.question_count),
                    { style: 'percent' }
                  )
                }}
              </span>
            </td>
          </tr>
        </transition-group>
      </template>
    </CoreTable>
  </div>
</template>
  
  
  <script>
  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import commonCoach from '../common';
  
  export default {
    name: 'ReportsAssessmentDetailTable',
    mixins: [commonCoach, commonCoreStrings],
    props: {
      entries: {
        type: Array,
        default: () => [],
      },
    },
    computed: {
    },
    methods: {
      calcPercentage(score, total) {
        return (score / total);
      },
      scoreColor(value) {
        console.log({ value })
        if (value <= 0) {
          return '#D9D9D9';
        }
        if (value > 0 && value <= 0.25) {
          return '#FF412A';
        }
        if (value > 0.25 && value <= 0.50) {
          return '#EC9090';
        }
        if (value > 0.50 && value <= 0.69) {
          return '#F5C216';
        }
        if (value > 0.69 && value <= 0.74) {
          return '#99CC33';
        }
        if (value <= 1) {
          return '#00B050';
        }
        if (value > 1) {
          return 'black';
        }
      },
    },
    $trs: {
      scoreLabel: {
        message: 'Score',
        context: '',
      },
      emptyMessage: {
        message: 'Test breakdown list is empty',
        context: '',
      }
    },
  };
  
  </script>
  
  
  <style lang="scss" scoped>
  @import '../common/print-table';
  
  .small-answered-count {
    display: block;
    margin-left: 1.75rem;
    /* matches KLabeledIcon */
    font-size: small;
  }
  
  .score-chip {
    display: inline-flex;
    padding: 4px 8px;
    align-items: center;
    justify-content: center;
    border-radius: 50px;
    min-width: 100px;
  }
  .back-row {
    display: inline-flex;
    gap: 6px;
    cursor: pointer;
    & span {
      text-decoration: underline;
    }
  }
  </style>