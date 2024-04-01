<template>

  <Block
    :allLinkText="coachString('viewAllAction')"
    :allLinkRoute="classRoute('ReportsAssessmentListPage', {})"
    :showAllLink="listData.length > 0"
  >
    <template #title>
      <KLabeledIcon icon="quiz" :label="coreString('assessmentLabel')" />
    </template>
  
    <p v-if="listData.length === 0">
      {{ coachString('assessmenListEmptyState') }}
    </p>

    <BlockItem
      v-for="item in listData"
      :key="item.key"
    >
      <router-link
        class="link"
        :style="{ color: $themeTokens.text }"
        :class="themeClass"
        :to="classRoute('ReportsAssessmentLearnerListPage', { quizId: item.key })"
      >
        <KFixedGrid numCols="4" class="wrapper">
          <KFixedGridItem span="3">
            <h3 class="title">
              {{ item.name }}
            </h3>
            <div class="context2">
              <Recipients
                :groupNames="item.learner"
                :hasAssignments="item.learner.length"
              />
            </div>
          </KFixedGridItem>
          <KFixedGridItem span="1" alignment="right">
            <div class="context">
              <span>{{ learnerStatus(item) }}</span>
            </div>
          </KFixedGridItem>
        </KFixedGrid>
      </router-link>
    </BlockItem>
  </Block>
  
</template>
  
  
  <script>
  
    import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
    import commonCoach from '../../common';
    import Block from './Block';
    import BlockItem from './BlockItem';
  
    const MAX_QUIZZES = 3;
  
    export default {
      name: 'AssessmentBlock',
      components: {
        Block,
        BlockItem,
      },
      mixins: [commonCoach, commonCoreStrings],
      computed: {
        listData() {
          return this.assessmentGroups.slice(0, MAX_QUIZZES).map(assessment => {
            const learner = this.getRecipientNameForAssessment(assessment);
            return {
              key: assessment.id,
              name: assessment.title,
              learner,
              isActive: assessment.active,
              isArchive: assessment.archive,
            }
          })
        },
        themeClass() {
          return this.$computedClass({
            ':hover': {
              // Background is light enough so that contents colored at grey.v_300
              // are still visible.
              backgroundColor: this.$themePalette.grey.v_100,
              // Add equal and opposite margin and padding to give the highlighted
              // region more space without increasing the size of the parent div.
              margin: '-8px',
              padding: '8px',
              borderRadius: '4px',
            },
          });
        },
      },
      methods: {
        learnerStatus(assessment) {
          if (assessment.isActive && !assessment.isArchive) {
            return 'Started'
          }
          if (assessment.isActive && assessment.isArchive) {
            return 'Completed'
          }
          return 'Not Started'
        }
      },
    };
  
  </script>
  
  
  <style lang="scss" scoped>
  .link {
    display: block;
    text-decoration: none;
  }
  .wrapper {
    margin-bottom: 8px;
  }
  .title {
    margin-bottom: 0;
  }
  .context2 {
    margin-top: 8px;
    font-size: small;
  }
  .context {
    position: relative;
    top: 16px;
    margin-bottom: 16px;
    font-size: small;
  }
</style>
  