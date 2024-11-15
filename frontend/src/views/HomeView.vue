<template>
  <NavBar />
  <div class="container mt-3">
    <div v-if="user">
      <h2>Welcome {{ user.username }}</h2>
    </div>
    <div v-else>
      <h2>Welcome please Login</h2>
    </div>

    <!-- SERACH BAR -->
    <div class="form-group mt-5 mb-3">
      <input type="text" class="form-control" id="search" v-model="searchQuery" placeholder="Search for products here!">
    </div>

    <div v-for="category in filteredCategories" :key="category.id">
      <h4>{{ category.name }}</h4>
      <p>{{ category.description }}</p>
      <div class="row">
        <div v-for="product in category.products" :key="product.id" class="col-md-3 mb-3">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">{{ product.name }}</h5>
              <p class="card-text">Rs. {{ product.price }}/{{ product.unit }}</p>
              <div v-if="role === 'user'">
              <input type="number" v-model="quantities[product.id]" class="form-control mb-2" placeholder="Quantity">
              <button @click="addToCart(product.id, quantities[product.id] || 1)" class="btn btn-primary btn-block">
                Add to Cart
              </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// @ is an alias to /src
import NavBar from '@/components/NavBar.vue';
import userMixin from '@/mixins/userMixin';
export default {
  name: 'HomeView',
  mixins: [userMixin],
  components: {
    NavBar
  },
  data() {
    return {
      categories: [],
      searchQuery: '',
      quantities: {}
    }
  },

  async created() {
    await this.getData();
  },

  computed: {
    filteredCategories() {
      const searchTerm = this.searchQuery.toLowerCase();
      return this.categories.map(category => {
        const filteredProducts = category.products.filter(product =>
          product.name.toLowerCase().includes(searchTerm)
        );
        return { ...category, products: filteredProducts };
      }).filter(category => category.products.length > 0);
    }
  },

  methods: {
    async getData() {
      const response = await fetch('http://localhost:5000/product', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      const data = await response.json()
      // console.log(data)
      if (!response.ok) {
        console.log("Something went wrong!")
      }
      else {
        this.categories = data;
      }
    },
    async addToCart(productId, quantity) {
      console.log(productId, quantity);
      try {
        const response = await fetch('http://localhost:5000/add-to-cart', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({
            product_id: productId,
            quantity: quantity
          })
        });
        const data = await response.json();
        if (response.ok) {
          alert(data.message);
          this.quantities = {};
        } else {
          alert(data.error);
        }
      } catch (error) {
        console.error("Error adding product to cart:", error);
      }
    }
  }

}
</script>
