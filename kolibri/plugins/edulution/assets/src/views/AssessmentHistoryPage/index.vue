<template>
  <LearnAppBarPage :appBarTitle="learnString('learnLabel')">
    <div style="display: flex; justify-content: space-between;align-items: center;margin-top:8px;">
      <div style="display: flex; gap:30px;align-items: end;">
        <p 
          class="select-date"
          @click.prevent="openDateRangeModal"
        >
          {{ showDateText }}
        </p>
        <KDateRange 
          v-if="ShowDateRangeModal"
          :firstAllowedDate="firstAllowedDate"
          :lastAllowedDate="lastAllowedDate"
          :submitText="$tr('submitText')"
          :cancelText="coreString('cancelAction')"
          title="Select a date Range"
          startDateLegendText="Start Date"
          endDateLegendText="End Date"
          @cancel="openDateRangeModal"
          @submit="onSubmit"
        />
        <KSelect 
          v-model="selectedItem"
          :style="{ minWidth: '200px' }"
          :options="selectOptions"
          label="Assessment Dropdown"
        />
      </div>

      <KButtonGroup>
        <KButton
          :text="'Apply Filter'"
          primary
          @click.prevent="onApplyFilter"
        />
        <KButton
          appearance="raised-button"
          text="Reset Filter"
          :disabled="isResetButtonDisabled"
          @click.prevent="onClear"
        />
      </KButtonGroup>
    </div>

    <div v-if="tableData && tableData.length">
      <CoreTable :emptyMessage="$tr('emptyMessage')" :style="{ backgroundColor: 'white',marginBottom: '10px' }">
        <template #headers>
          <th>
            {{ $tr('DateLabel') }}
          </th>
          <th>{{ $tr('title') }}</th>
          <th>{{ $tr('questions') }}</th>
          <th>{{ $tr('answers') }}</th>
          <th>{{ $tr('PercentageLabel') }}</th>
          <th>{{ $tr('attemptLabel') }}</th>
        </template>
        <template #tbody>
          <transition-group tag="tbody" name="list">
            <tr v-for="(tableRow, index) in tableData" :key="tableRow.assessment_id">
              <td>
                {{ formatDate(tableRow.date) }}
              </td>
              <td>
                {{ tableRow.title }}
              </td>
              <td>{{ tableRow.question_count }}</td>
              <td>{{ tableRow.answer_count }}</td>
              <td>
                <span
                  class="score-chip"
                  :style="{
                    backgroundColor: scoreColor(
                      calcPercentage(tableRow.answer_count, tableRow.question_count)
                    ),
                    color: 'white',
                  }"
                >
                  {{
                    $formatNumber(
                      calcPercentage(tableRow.answer_count, tableRow.question_count),
                      { style: 'percent' }
                    )
                  }}
                </span>
              </td>
              <td>{{ ordinalNumber(tableRow.attempts) }}</td>
            </tr>
          </transition-group>
        </template>
      </CoreTable>
      <Pagination
        :currentPage="currentPage"
        :totalPages="totalPages" 
        @pageChanged="onApplyPagination"
      />
    </div>
    <div v-if="showloading">
      Loading...
    </div>
  </LearnAppBarPage>
</template>

<script>
import { mapGetters } from 'vuex';
import { now } from 'kolibri.utils.serverClock';
import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
import CoreTable from 'kolibri.coreVue.components.CoreTable';
import { AssessmentHistoryReport,AssessmentList } from 'kolibri.resources';
import LearnAppBarPage from '../LearnAppBarPage';
import Pagination from '../Pagination.vue';
import commonLearnStrings from './../commonLearnStrings';

export default {
    name: 'AssessmentHistoryPage',
    metaInfo() {
      return {
        title: this.learnString('learnLabel'),
      };
    },
    components:{LearnAppBarPage,CoreTable, Pagination},
    mixins: [commonLearnStrings,commonCoreStrings],
    data(){
        return {
            selectedItem: { label: 'All', value: 0},
            selectOptions: { label: 'All', value: 0},
            ShowDateRangeModal:false,
            firstAllowedDate:null,
            lastAllowedDate:now(),
            getStartDate:null,
            getEndDate:null,
            showDateText: 'Select Date',
            currentPage:1,
            totalPages:1,
            tableData: [],
            pageLimit: 10,
            isResetButtonDisabled:true,
            showloading:false
        }
    },
    computed: {
      ...mapGetters(['currentUserId']),
    },
    async beforeMount() {
      await this.fetchDropdwnList()
      await this.fetchTableData() 
      },
    methods:{
      async fetchDropdwnList(){
        const response = await AssessmentList.fetchModel({ id: this.currentUserId})  

        this.selectOptions =[
          { label: 'All', value: 0 },
        ...response?.list.map(item => ({
          label: item.label,
          value: item.value
        }))
        ]
      },
      async fetchTableData(){
        this.showloading = true
        const params={
          from_date: this.getStartDate,
          to_date: this.getEndDate,
          assessment_id: this.selectedItem?.value === 0 ? null : this.selectedItem?.value,
          learner_ids:this.currentUserId,
          page_no:this.currentPage,
          page_limit:this.pageLimit ,
        }
       
        const response = await AssessmentHistoryReport.fetchModel({ id: this.currentUserId, getParams: params})
        this.tableData = response.list || []
        this.totalPages = Math.ceil(response?.total_count / this.pageLimit)
        this.showloading = false
      },
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
          const month = date.getMonth() + 1; 
          const year = date.getFullYear();

          return `${day}-${month}-${year}`;
        },
      onClear(){
        this.selectedItem = { label: 'All', value: 0 };
        this.getStartDate = null;
        this.getEndDate = null;
        this.showDateText = 'Select Date';
        this.currentPage = 1;
        this.fetchTableData()
      },
      openDateRangeModal() {
        this.ShowDateRangeModal = !this.ShowDateRangeModal
      },
      onSubmit(dates){
        this.getStartDate = new Date(dates.start.setHours(12, 0, 0, 0)).toISOString().split('T')[0];
        this.getEndDate = new Date(dates.end.setHours(12, 0, 0, 0)).toISOString().split('T')[0];
        this.showDateText = `${this.getStartDate} - ${this.getEndDate}`
        this.ShowDateRangeModal = !this.ShowDateRangeModal
      },
      async onApplyFilter() {
        this.currentPage = 1
        this.isResetButtonDisabled = false
        await this.fetchTableData()
      },
      async onApplyPagination(pageNumber) {
        this.currentPage = pageNumber
        await this.fetchTableData()
      },
      ordinalNumber(number) {
      const suffixes = ["th", "st", "nd", "rd"];
      const v = number % 100;
      return number + (suffixes[(v - 20) % 10] || suffixes[v] || suffixes[0]);
    }
    },
    $trs:{
      submitText:{
        message: 'Select'
      },
      PercentageLabel: {
          message: 'Percentage',
          context: '',
        },
        emptyMessage: {
          message: 'No Data Found',
          context: '',
        },
        DateLabel:{
          message: 'Date',
          context: '',
        },
        title:{
          message: 'Assessment Name',
          context: '',
        },
        questions:{
          message: 'Questions',
          context: '',
        },
        answers:{
          message: 'Answers',
          context: '',
        },
        attemptLabel:{
          message:"Attempts",
          context:""
        }
    }

}

</script>

<style lang="scss" scoped>
  @import '~kolibri-design-system/lib/styles/definitions';

  .select-date {
    padding: 2px 3px;
    border-bottom: 1px solid #0000001f;
    cursor: pointer;
    color:#000000DE,
  }

  .score-chip {
      display: inline-flex;
      padding: 4px 8px;
      align-items: center;
      justify-content: center;
      border-radius: 50px;
      min-width: 100px;
    }
  
    .loading {
    font-size: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 10px;
}
</style>