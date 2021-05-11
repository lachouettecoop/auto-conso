<template>
  <v-app id="app">
    <v-app-bar
      app
      color="primary"
      dark
      height="38"
    >
      <v-spacer></v-spacer>
      <v-btn :disabled="!token"
             small @click="logout()">
        Logout
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container>
        <Main/>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import Main from './components/Main.vue';

export default {
  name: 'App',
  components: {
    Main,
  },
  computed: {
    token() {
      return this.$store.state.authentication.token;
    },
  },
  methods: {
    logout() {
      this.$store.dispatch('authentication/logout');
    },
  },
};
</script>

<style>
</style>
