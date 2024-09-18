<template>

  <div class="sign-in-text">
    <div>
      {{ userString('signingInLabel') }}
    </div>
  </div>

</template>


<script>
  import commonUserStrings from '../commonUserStrings';

  export default {
    name: 'SignInHeading',
    mixins: [commonUserStrings],
  };

</script>


<style scoped lang="scss">

  .sign-in-text {
    margin-top: 24px;
    margin-bottom: 16px;
    text-align: center;
    font-weight: bold;
    color: rgb(7, 29, 73);
  }

</style>
