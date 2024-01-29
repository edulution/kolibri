<template>

  <CoachAppBarPage
    :authorized="userIsAuthorized"
    authorizedRole="adminOrCoach"
    :showSubNav="true"
  >

    <KPageContainer>
      <ReportsHeader
        :activeTabId="ReportsTabs.ATTENDANCE"
        :title="$isPrint ? $tr('printLabel', { className }) : null"
      />
      <KTabsPanel
        :tabsId="REPORTS_TABS_ID"
        :activeTabId="ReportsTabs.ATTENDANCE"
      >
        <div class="filter-row">
          <KSelect
            v-model="filter"
            :label="coachString('filterGroupsStatus')"
            :options="filterOptions"
            :inline="true"
          />
          <FilterTextbox
            v-model="filterInput"
            placeholder="Filter by username or fullname"
          />
        </div>

        <CoreTable :emptyMessage="emptyMessage">
          <template #headers>
            <th>{{ coachString('usernameLabel') }}</th>
            <th>{{ coachString('fullnameLabel') }}</th>
            <th>{{ coachString('statusLabel') }}</th>
            <th>{{ coachString('lastLoggedInLabel') }}</th>
            
          </template>
          <template #tbody>
            <transition-group
              tag="tbody"
              name="list"
            >
              <tr
                v-for="tableRow in table"
                :key="tableRow.id"
              >
                <td>
                  <KRouterLink
                    :text="tableRow.username"
                    :to="classRoute('ReportsLearnerReportPage', { learnerId: tableRow.id })"
                    icon="person"
                  />
                </td>
                <td>
                  {{ tableRow.name }}
                </td>
                
                <td>
                  <span>
                    <span class="labeled-icon-wrapper" :class="{ active: tableRow.isActiveLearner }">
                      <div class="icon">
                        <svg
                          role="presentation"
                          focusable="false"
                          xmlns="http://www.w3.org/2000/svg"
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            cx="12"
                            cy="12"
                            r="10"
                          />
                        </svg>
                      </div>
                      <div v-if="tableRow.isActiveLearner" dir="auto" class="label">Active</div>
                      <div v-else dir="auto" class="label">Inactive</div>
                    </span>
                  </span>
                </td>
                <td>
                  <KOptionalText
                    :text="
                      tableRow.lastInteractionTimestamp ? $formatDate(tableRow.lastInteractionTimestamp, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }) : '-'"
                  />
                </td>
              </tr>
            </transition-group>
          </template>
        </CoreTable>
      </KTabsPanel>
    </KPageContainer>
  </CoachAppBarPage>

</template>


<script>

  import FilterTextbox from 'kolibri.coreVue.components.FilterTextbox';
  import commonCoach from '../common';
  import { REPORTS_TABS_ID, ReportsTabs } from '../../constants/tabsConstants';
  import CoachAppBarPage from '../CoachAppBarPage';
  import ReportsHeader from './ReportsHeader';

  export default {
    name: 'ReportsAttendanceListPage',
    components: {
      CoachAppBarPage,
      ReportsHeader,
      FilterTextbox,
    },
    mixins: [commonCoach],
    data() {
      return {
        filter: '',
        REPORTS_TABS_ID,
        ReportsTabs,
        filterInput: '',
      };
    },
    computed: {
      emptyMessage() {
        if (this.filter.value === 'allGroups') {
          return this.coachString('attendanceListEmptyState');
        }
        if (this.filter.value === 'visibleGroups') {
          return this.coreString('noResultsLabel');
        }
        if (this.filter.value === 'groupsNotVisible') {
          return this.coreString('noResultsLabel');
        }
        return '';
      },
      filterOptions() {
        return [
          {
            label: this.coachString('filterGroupsAll'),
            value: 'all',
          },
        ];
      },
      table() {
        let sorted = this.learners.map(l => ({
          ...l,
          isActiveLearner: this.activeLearners.includes(l.id),
          lastInteractionTimestamp: this.learnersInfo.find(d => d.user__username === l.username)?.last_interaction_timestamp__max,
        }));
        
        if (this.filterInput) {
          const matchString = this.filterInput.toLowerCase();
          sorted = sorted.filter((learner) => {
            if (learner.name.toLowerCase().includes(matchString)
              || learner.username.toLowerCase().includes(matchString)) {
              return true;
            }
            return false;
          })
        }

        return sorted;
      },
    },
    $trs: {
      printLabel: {
        message: '{className} Learners',
        context:
          "Title that displays on a printed copy of the 'Reports' > 'Learners' page. This shows if the user uses the 'Print' option by clicking on the printer icon.",
      },
    },
  };

</script>


<style lang="scss" scoped>

  @import '../common/print-table';

  .filter-row {
    display: flex;
    align-items: center;
  }
  .labeled-icon-wrapper {
    position: relative;
    display: inline-block;
    .icon {
    position: absolute;
    left: 0;
      svg {
        position: relative;
        top: 0.125em;
        width: 1.125em;
        height: 1.125em;
        fill: rgb(224, 224, 224) !important;
      }
    }

    .label {
      display: block;
      margin-left: 1.925em;
      color: rgb(224, 224, 224);
    }

    &.active {
      .icon {
        svg {
          fill: green !important;
        }
      }
      .label {
        color: rgb(33, 33, 33);
      }
    }
  }
</style>
