<template>
  <v-card align="center">
    <v-alert v-model="alert.show" dense dismissible type="error">
      {{alert.message}}
    </v-alert>
    <v-card-text><img src="@/assets/logo.png"></v-card-text>
    <v-card-text>
      <v-container fluid>
        <v-layout column>
          <form>
            <v-text-field v-model="email"
                          label="E-mail"
            ></v-text-field>
            <v-text-field v-model="password"
                          label="Password"
                          :append-icon="showPassword ? 'fa-eye-slash' : 'fa-eye'"
                          :type="showPassword ? 'text' : 'password'"
                          @click:append="showPassword = !showPassword"
            ></v-text-field>
            <v-btn color="teal darken-3"
                   class="white--text"
                   :disabled="!email || !password || submitted"
                   @click="login()">
                Valider
            </v-btn>
          </form>
        </v-layout>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script>

export default {
  data() {
    return {
      email: '',
      password: '',
      showPassword: false,
      submitted: false,
      alert: {
        show: false,
        message: '',
      },
    };
  },
  created() {
    this.$store.dispatch('authentication/logout');
  },
  methods: {
    login() {
      this.submitted = true;
      this.$store.dispatch({
        type: 'authentication/login',
        email: this.email,
        password: this.password,
      }).catch((error) => {
        this.alert.message = error.response.data;
        this.alert.show = true;
      }).finally(() => {
        this.submitted = false;
      });
    },
  },
};

</script>
