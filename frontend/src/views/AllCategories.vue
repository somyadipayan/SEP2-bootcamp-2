<template>
<NavBar/>
<div class="container mt-5">
    <h1>All Categories</h1>
    <table class="table">
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Advertisement</th>
                <th v-if="role==='admin'">Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="category in categories" :key="category.id">
                <td>{{ category.name }}</td>
                <td>{{ category.description }}</td>
                <td><a :href="`http://localhost:5000/category/${category.id}/advertisement`" class="btn btn-light" target="_blank">View</a></td>
                <td v-if="role==='admin'">
                    <div class="btn-group">
                    <button class="btn btn-danger" @click="deleteCategory(category.id)">DELETE</button>
                    <router-link :to="`/update-category/${category.id}`" class="btn btn-primary">UPDATE</router-link>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
    <router-link v-if="role==='admin'" to="/create-category" class="btn btn-dark">Create Category</router-link>
</div>
<!-- testing -->
<!-- <embed class="mt-5" src="http://localhost:5000/category/5/advertisement#toolbar=0" type="application/pdf" width="100%" height="600px"> -->
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import userMixin from '@/mixins/userMixin';
export default {
    mixins: [userMixin],
    name: "AllCategories",
    components: {
        NavBar
    },
    data() {
        return {
            categories: []
        }
    },
    async mounted() {
        await this.getCategories()
    },
    methods: {
        async getCategories() {
            const response = await fetch('http://localhost:5000/categories',{
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            const data = await response.json()
            this.categories = data.categories
        },
        async deleteCategory(id) {
            const response = await fetch(`http://localhost:5000/category/${id}`,{
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            })
            const data = await response.json()
            if(!response.ok){
                alert(data.error)
            }
            else{
                alert(data.message)
                this.getCategories()
            }
        }
    }
}


</script>