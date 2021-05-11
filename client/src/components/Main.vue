<template>
  <v-container class="justify-center" style="align-items: center">
    <v-dialog
      v-model="showLogin"
      fullscreen
      hide-overlay
    >
      <Login/>
    </v-dialog>
    <v-dialog
      v-model="showSummary"
      width="50%"
      persistent
    >
      <Summary :losses="losses"
               @cancel="showSummary=false"
               @lossesRecorded="lossesRecorded()"
      />
    </v-dialog>
    <v-alert v-model="alert.show" dismissible type="error">
      {{alert.message}}
    </v-alert>
    <template v-if="productsLoading">
      <v-row class="justify-center text-center">
        <h2>La mise à jour des produits peut prendre un certain temps.<br/>Merci de patienter.</h2>
      </v-row>
      <v-row class="justify-center">
        <v-progress-circular
          indeterminate
          :size="100"
          :width="7"
          color="primary"
        />
      </v-row>
    </template>
    <template v-else>
      <v-row justify="center">
        <v-col cols="9">
          <v-autocomplete
            clearable
            rounded
            solo
            v-model="product"
            label="Nom du produit"
            :items="products"
            item-text="name"
            return-object
            :filter="filter"
          ></v-autocomplete>
        </v-col>
        <v-col cols="3">
          <v-autocomplete
            clearable
            rounded
            solo
            v-model="product"
            label="Code Barre"
            :items="products"
            item-text="barcode"
            return-object
          ></v-autocomplete>
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-col cols="6">
          <v-radio-group
            v-model="lossType"
            mandatory
            row
          >
            <v-radio
              label="Auto-consomation"
              value="autoconso"
            ></v-radio>
            <v-radio
              label="Hygiène"
              value="hygiene"
            ></v-radio>
            <v-radio
              label="Perte"
              value="loss"
            ></v-radio>
          </v-radio-group>
        </v-col>
        <v-col cols="3">
          <v-text-field :label="isVariableWeightProduct(product)?'Poids en gramme':'Quantité'"
                        rounded
                        solo
                        v-model="quantity"
                        :disabled="!product"
          ></v-text-field>
        </v-col>
        <v-col cols="1">
          <v-btn
            :disabled="!(product && quantity > 0)"
            @click="addLost"
            rounded
          >
            Valider
          </v-btn>
        </v-col>
      </v-row>
      <v-row justify="center">
        <p v-if="isVariableWeightProduct(product)" >
          ⚠️ Produit à poids variable. Veuillez rentrer un poids en gramme.
        </p>
      </v-row>
      <v-row justify="center" class="pb-4">
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
                <th>
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
                <td>
                  <v-btn icon @click="removeLost(index)">
                    <v-icon>mdi-trash-can-outline</v-icon>
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-row>
      <v-row justify="center" class="pt-4">
        <v-btn
          :disabled="losses.length <= 0"
          @click="showSummary=true"
          rounded
          width="300px"
        >
          Enregistrer dans Odoo
        </v-btn>
      </v-row>
    </template>
  </v-container>
</template>

<script>
import Login from './Login.vue';
import Summary from './Summary.vue';

export default {
  name: 'Main',
  components: {
    Login,
    Summary,
  },
  data: () => ({
    showLogin: true,
    showSummary: false,
    showQuantitySelection: true,
    product: null,
    losses: [],
    lossType: 'loss',
    quantity: null,
    alert: {
      show: false,
      message: '',
    },
  }),
  watch: {
    token() {
      if (this.token) {
        this.$store.dispatch({
          type: 'odoo/getProducts',
          token: this.token,
        });
        this.showLogin = false;
      } else {
        this.showSummary = false;
        this.showLogin = true;
      }
    },
    productsError() {
      if (this.productsError) {
        this.alert.message = this.productsError;
        this.alert.show = true;
      }
    },
  },
  computed: {
    token() {
      return this.$store.state.authentication.token;
    },
    products() {
      return this.$store.state.odoo.products;
    },
    productsLoading() {
      return this.$store.state.odoo.loading;
    },
    productsError() {
      return this.$store.state.odoo.error;
    },
  },
  methods: {
    filter(_, queryText, itemText) {
      const query = queryText.toLocaleLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '');
      const item = itemText.toLocaleLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '');
      return item.indexOf(query) > -1;
    },
    isVariableWeightProduct(product) {
      if (!product) {
        return false;
      }
      return String(product.barcode).startsWith('260');
    },
    addLost() {
      this.losses.push({
        product: this.product,
        quantity: this.isVariableWeightProduct(this.product) ? this.quantity / 1000 : this.quantity,
        lossType: this.lossType,
      });
      this.quantity = null;
      this.product = null;
      this.lossType = 'loss';
    },
    removeLost(index) {
      if (index > -1 && this.losses.length > index) {
        this.losses.splice(index, 1);
      }
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
    lossesRecorded() {
      this.losses = [];
      this.showSummary = false;
    },
  },
};
</script>
