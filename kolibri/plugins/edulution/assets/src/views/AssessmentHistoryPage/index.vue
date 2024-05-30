<template>
  <LearnAppBarPage :appBarTitle="learnString('learnLabel')">
    <div style="display: flex; justify-content: space-between;align-items: center;">
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
          :disabled="isApplyButtonDisabled"
          @click.prevent="onApplyFilter"
        />
        <KButton
          appearance="raised-button"
          text="Reset Filter"
          @click.prevent="onClear"
        />
      </KButtonGroup>
    </div>

    <div>
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
        @pageChanged="onApply"
      />
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
            selectedItem: null,
            selectOptions: { label: 'All', value: 0},
            ShowDateRangeModal:false,
            firstAllowedDate:null,
            lastAllowedDate:now(),
            getStartDate:null,
            getEndDate:null,
            showDateText: 'Select Date',
            currentPage:1,
            totalPages:1,
            selectLabel:"Assessment Dropdwon",
            tableData: [],
            pageLimit: 10,
        }
    },
    computed: {
      ...mapGetters(['currentUserId']),
      isApplyButtonDisabled() {
          return !this.selectedItem && !this.getStartDate && !this.getEndDate;
    },
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
        this.selectLabel="Assessment Dropdown"
        this.currentPage = 1;
        this.fetchTableData()
      },
      openDateRangeModal() {
        this.ShowDateRangeModal = !this.ShowDateRangeModal
      },
      onSubmit(dates){
        this.getStartDate = dates.start?.toISOString().split('T')[0];
        this.getEndDate = dates.end?.toISOString().split('T')[0];
        this.showDateText = `${this.getStartDate} - ${this.getEndDate}`
        this.ShowDateRangeModal = !this.ShowDateRangeModal
      },
      async onApplyFilter() {
        this.currentPage = 1
        await this.fetchTableData()
      },
      async onApply(pageNumber) {
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
          message: 'Assessment Historical',
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
    padding: 2px 8px;
    border: 1px solid grey;
    cursor: pointer;
    border-radius: 5px;
  }

  .score-chip {
      display: inline-flex;
      padding: 4px 8px;
      align-items: center;
      justify-content: center;
      border-radius: 50px;
      min-width: 100px;
    }
</style>