<template>
  <nav class="pagination">
    <ul>
      <li :class="{ disabled: currentPage === 1 }" @click.prevent="changePage(1)">
        <span>&laquo;&laquo;</span>
      </li>
      <li :class="{ disabled: currentPage === 1 }" @click.prevent="changePage(currentPage - 1)">
        <span>&laquo;</span>
      </li>
      <span>{{ currentPage }}/{{ totalPages }}</span>
      <li :class="{ disabled: currentPage === totalPages }" @click.prevent="changePage(currentPage + 1)">
        <span>&raquo;</span>
      </li>
      <li :class="{ disabled: currentPage === totalPages }" @click.prevent="changePage(totalPages)">
        <span>&raquo;&raquo;</span>
      </li>
    </ul>
  </nav>
</template>

<script>
export default {
  name: 'Pagination',
  props: {
    currentPage: {
      type: Number,
      required: true,
    },
    totalPages: {
      type: Number,
      required: true,
    },
  },
  methods: {
    changePage(page) {
      if (page !== this.currentPage && page <= this.totalPages) {
       
        this.$emit('pageChanged', page);
      }
    },
  },
};
</script>

<style scoped>
.pagination ul {
  display: flex;
  list-style: none;
  padding: 0;
  align-items: center;
  justify-content: flex-end;
}

.pagination li {
  margin: 0 5px;
  padding: 5px 10px;
  cursor: pointer;
  border: 1px solid #ccc;
}

.pagination li.disabled {
  pointer-events: none;
  color: #ccc;
}

.pagination li.active {
  background-color: #007bff;
  color: white;
}
</style>
