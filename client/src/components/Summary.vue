<template>
  <v-card class="pa-4" align="center" justify="center">
    <v-card-title class="pa-4 text-center align-center justify-center"
                  align="center" justify="center">
      Vous êtes sur le point d'enregistrer les pertes suivantes
    </v-card-title>
    <v-card-text>
      <v-simple-table style="width: 100%">
        <template v-slot:default>
          <thead>
            <tr>
              <th class="text-left">
                Nom du produit
              </th>
              <th class="text-left">
                Quantité
              </th>
              <th class="text-left">
                Type
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(item, index) in losses"
              :key="index"
            >
              <td>{{ item.product.name }}</td>
              <td v-if="isVariableWeightProduct(item.product)">{{ item.quantity * 1000 }} g</td>
              <td v-else>{{ item.quantity }}</td>
              <td>{{ lossName(item.lossType) }}</td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-card-text>
    <v-card-actions style="justify-content: center">
      <v-btn
        :disabled="recordInProgress"
        @click="$emit('cancel')"
        rounded
        width="300px"
      >
        Annuler
      </v-btn>
      <v-btn
        :disabled="recordInProgress"
        @click="recordsLosses"
        rounded
        width="300px"
      >
        <template v-if="!recordInProgress">Enregistrer dans Odoo</template>
        <v-progress-circular
          v-else
          indeterminate
          color="primary"></v-progress-circular>
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import axios from 'axios';
import serverUrl from '../mixin/url';
import authHeader from '../mixin/authHeader';

export default {
  name: 'Summary',
  props: {
    losses: Array,
  },
  data: () => ({
    recordInProgress: false,
    alert: {
      show: false,
      message: '',
    },
  }),
  computed: {
    token() {
      return this.$store.state.authentication.token;
    },
  },
  methods: {
    isVariableWeightProduct(product) {
      if (!product) {
        return false;
      }
      return String(product.barcode).startsWith('260');
    },
    lossName(lossType) {
      if (lossType === 'loss') {
        return 'Perte';
      }
      if (lossType === 'autoconso') {
        return 'Auto-consomation';
      }
      return 'Hygiène';
    },
    recordsLosses() {
      this.recordInProgress = true;
      axios({
        method: 'post',
        url: `${serverUrl()}/losses`,
        headers: authHeader(this.token),
        data: this.losses,
      }).then(() => {
        this.$emit('lossesRecorded');
      }).catch((error) => {
        this.alert.message = error;
        this.alert.show = true;
      }).finally(() => {
        this.recordInProgress = false;
      });
    },
  },
};
</script>

<style scoped>

</style>
