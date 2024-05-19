<template>
  <div v-if="!assessmentArray.length" class="loading">
    Loading...
  </div>
  <div v-else>
    <div :style="{ display: 'flex' , gap: '16%' }">
      <p>Title</p>
      <p>Limit</p>
      <p>Value</p>
    </div>
    <div 
      v-for="tableD of assessmentArray" 
      :key="tableD.id"
    >
      <div :style="{ display: 'flex' ,gap: '10%' }">
        <p>
          {{ tableD.title }}
        </p>
        <p>
          {{ tableD.limit }}
        </p>
        <KTextbox
          v-model="tableD.value"
          :label="'Enter Count'"
          type="number"
          @input="validateLevelInput(tableD)"
        />
        <p>{{ tableD.errorMessage }}</p>
      </div>

      <div 
        v-for="topicData of tableD.exercises" 
        :key="topicData.id"
        :style="{ display: 'flex' ,gap: '10%' }"
      >
        <p>{{ topicData.title }}</p>
        <p>{{ topicData.limit }}</p>
        <KTextbox
          v-model="topicData.value"
          :label="'Enter Count'"
          type="number"
          @input="updateExerciseValue(tableD,topicData)"
        />
        <p>{{ topicData.errorMessage }}</p>
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

      data.value = totalValue;
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
  

</style>





