<template>
  <div v-if="!assessmentArray.length" class="loading">
    Loading...
  </div>
  <div v-else style="max-width: 720px;">
    <div :style="{ display: 'flex' , gap: '30px' }">
      <p style="flex: 1 1 auto;">Title</p>
      <p style="flex: 0 1 auto;">Limit</p>
      <p style="flex: 0 0 220px;">Value</p>
    </div>
    <div 
      v-for="tableD of assessmentArray" 
      :key="tableD.id"
      style="border: 1px solid #CCC; border-radius: 4px; margin-bottom: 12px;"
    >
      <div :style="{ display: 'flex' , gap: '30px', padding: '12px', paddingBottom: 0 }">
        <p style="flex: 1 1 auto;">
          {{ tableD.title }}
        </p>
        <p style="flex: 0 1 auto;">
          {{ tableD.limit }}
        </p>
        <div
          style="flex: 0 0 220px; display: flex; align-items: center;"
        >
          <KTextbox
            v-model="tableD.value"
            :label="'Enter Count'"
            type="number"
            :invalid="tableD.errorMessage"
            :invalidText="tableD.errorMessage"
            @input="validateLevelInput(tableD)"
          />

          <KIconButton
            :icon="expandedRowIds.includes(tableD.id) ? 'chevronUp' : 'chevronDown'"
            size="small"
            type="secondary"
            class="toggle"
            @click="handleTableExpansionClick(tableD.id)"
          />
        </div>
      </div>

      <div 
        v-for="topicData of tableD.exercises" 
        :key="topicData.id"
        :style="{ display: expandedRowIds.includes(tableD.id) ? 'flex' : 'none',
                  gap: '30px', backgroundColor: 'whitesmoke',
                  borderRadius: '4px', padding: '12px', paddingBottom: 0 
        }"
      >
        <p style="flex: 1 1 auto;">{{ topicData.title }}</p>
        <p style="flex: 0 1 auto;">{{ topicData.limit }}</p>
        <div
          style="flex: 0 0 220px;"
        >
          <KTextbox
            v-model="topicData.value"
            :label="'Enter Count'"
            type="number"
            :invalid="topicData.errorMessage"
            :invalidText="topicData.errorMessage"
            @input="updateExerciseValue(tableD,topicData)"
          />
        </div>
      </div>
    </div>
  </div>
</template>



<script>
import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
import commonCoach from '../../common';

export default {
  name: 'ChannelTable',
  mixins: [commonCoach, commonCoreStrings],
  props: {
    tableData: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      assessmentArray: [],
      expandedRowIds: [],
    };
  },

  watch: {
   tableData : {
    immediate : true,
    handler(newVal) {
      newVal.forEach(item => {
 
         const newExercises = item.exercises.map(exercise => {
          const maxCount = item.question_sources.filter(i => i.exercise_id === exercise.id).length
          return{
            id: exercise.id,
            title: exercise.title,
            limit: maxCount,
            errorMessage:'',
            value:maxCount
          }
        });

        this.assessmentArray.push({
          id: item.id,
          title: item.title,
          limit: item.question_count,
          errorMessage: '',
          exercises: newExercises,
          value:item.question_count
        })
        });
    }
   }

  },
  methods:{
    handleTableExpansionClick(tableRowId) {

    const index = this.expandedRowIds.indexOf(tableRowId);
    if (index === -1) {
      // Add the ID to the array
      this.expandedRowIds.push(tableRowId);
    } else {
      // Remove the ID from the array
      this.expandedRowIds.splice(index, 1);
    }

  },
    validateLevelInput(data) {
      
      let limitValue = parseInt(data.value)

        if(limitValue > data.limit) {
          limitValue = data.limit;
          data.errorMessage = `Limit cannot exceed ${data.limit}`;
        } else if(limitValue <= 0){
          limitValue = data.limit;
          data.errorMessage = 'Limit cannot be less than 0';
        }
        else{
          data.errorMessage = '';
          data.value = limitValue;
        }

        const numExercises = data.exercises.length;
        if (numExercises > 0) {
          const equalValue = Math.floor(limitValue / numExercises);
          const remainder = limitValue % numExercises;

          data.exercises.forEach((exercise, index) => {
            if (index < remainder) {
              exercise.value = equalValue + 1; 
            } else {
              exercise.value = equalValue;
            }
          });
        }
        this.$emit('update-new-data', this.assessmentArray);
    },
    updateExerciseValue(data, topicData) {

      let totalValue = 0;
      data.exercises.forEach(exercise => {
        totalValue += parseInt(exercise.value);
      });

      if (totalValue > data.limit) {
        topicData.errorMessage = `Total cannot exceed ${topicData.limit}`;
        topicData.value = data.limit - (totalValue - parseInt(topicData.value)); 
      } else {
        topicData.errorMessage = '';
      }

      // data.value = totalValue;
      this.$emit('update-new-data', this.assessmentArray);
    }
  },
};
</script>

<style lang="scss" scoped>

.loading {
    font-size: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 25px;
    padding: 10px;
}
  
.toggle {
  margin-left: 8px;
}
</style>





