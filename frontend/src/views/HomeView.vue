<template>
  <NavBar/>
  <div class="home">
    <div v-if="this.isLoggedIn">
      <div v-if="user">
      <h2>Hi {{ user.username }}</h2>
      </div>
    </div>
    <div v-else="this.isLoggedIn">
      <h2>Please Log in to access our features</h2>
    </div>
    <img alt="Vue logo" src="../assets/logo.png">
    <HelloWorld msg="Welcome to Your Vue.js App"/>
  </div>
</template>

<script>
// @ is an alias to /src
import NavBar from '@/components/NavBar.vue';
import HelloWorld from '@/components/HelloWorld.vue'
import userMixin from '@/mixins/userMixin';
export default {
  name: 'HomeView',
  mixins: [userMixin],
  components: {
    HelloWorld, NavBar
  }
}
</script>
