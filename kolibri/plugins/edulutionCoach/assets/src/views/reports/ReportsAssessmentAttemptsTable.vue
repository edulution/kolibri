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
        <th>{{ $tr('AttemptNumberLabel') }}</th>
        <th>
          {{ $tr('DateLabel') }}
        </th>
        <th>
          {{ $tr('scoreLabel') }}
        </th>
        <th>
          {{ $tr('ActionLabel') }}
        </th>
      </template>
      <template #tbody>
        <transition-group tag="tbody" name="list">
          <tr v-for="(tableRow, index) in attemptHistory" :key="tableRow.assessment_id">
            <td>
              {{ tableRow.attempt_count }}
            </td>
            <td>
              <!-- <StatusElapsedTime :date="tableRow.start_timestamp" actionType="created" /> -->
              <!-- {{ tableRow.start_timestamp }} -->
              {{ formatDate(tableRow.start_timestamp) }}
            </td>
            <td>
              <span
                class="score-chip"
                :style="{
                  backgroundColor: scoreColor(
                    calcPercentage(tableRow.corrected_question_count, tableRow.question_count)
                  ),
                  color: 'white',
                }"
              >
                {{
                  $formatNumber(
                    calcPercentage(tableRow.corrected_question_count, tableRow.question_count),
                    { style: 'percent' }
                  )
                }}
              </span>
            </td>
            <td>
              <span class="btn-style">
                View Details
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
      name: 'ReportsAssessmentAttemptsTable',
      mixins: [commonCoach, commonCoreStrings],
      props: {
        attemptHistory:{
          type: Array,
          default: () => [],
        }
      },
      computed: {
      },
      methods: {
        calcPercentage(score, total) {
          return (score / total);
        },
        scoreColor(value) {
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
        formatDate(dateStr) {
          const date = new Date(dateStr);
          const day = date.getDate();
          const month = date.getMonth() + 1; // January is 0, so we add 1
          const year = date.getFullYear();

          return `${day}-${month}-${year}`;
        }
      },
      $trs: {
        scoreLabel: {
          message: 'Score',
          context: '',
        },
        emptyMessage: {
          message: 'Test breakdown list is empty',
          context: '',
        },
        DateLabel:{
          message: 'Date of Attempt',
          context: '',
        },
        ActionLabel:{
          message: 'Action',
          context: '',
        },
        AttemptNumberLabel:{
          message: 'Attempt Number',
          context: '',
        },
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

    .btn-style{
    color: blue  !important;
    cursor: pointer;
    border-radius: 8px;
    padding: 2px 9px;
    box-shadow: 0 2px 3px 1px rgba(0, 0, 0, 0.2);
  }
    </style>