<template>

  <img :src="image">

</template>


<script type="text/javascript">

  import logo from './edulution_map_only.svg';

  export default {
    name: 'CoreLogo',
    props: {
      src: {
        type: String,
        default: '',
      },
    },
    computed: {
      image() {
        return this.src && this.src.length ? this.src : logo;
      },
    },
  };

</script>
