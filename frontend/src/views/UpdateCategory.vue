<template>
    <NavBar />
    <div class="container mt-5">
        <h2>Update Category Here</h2>
        <form @submit.prevent="updateCategory">
            <div class="mb-3">
                <label for="name" class="form-label">Name</label>
                <input v-model="name" type="text" class="form-control" id="name">
            </div>
            <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <input v-model="description" type="text" class="form-control" id="description">
            </div>
            <div class="mb-3">
                <label for="advertisement" class="form-label">Advertisement</label>
                <input type="file" class="form-control" id="advertisement" @change="handlefileChange" accept=".pdf" >
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
export default {
    name: "UpdateCategory",
    components: {
        NavBar
    },
    mounted() {
        const category_id = this.$route.params.id;
        this.getCategory(category_id);
    },
    
    data() {
        return {
            name: "",
            description: "",
            advertisement: null
        }
    },
    methods: {
        handlefileChange(event) {
            console.log("File changed")
            console.log(event)
            this.advertisement = event.target.files[0];
        },
        async updateCategory() {
            const formData = new FormData();
            const category_id = this.$route.params.id;
            formData.append("name", this.name);
            formData.append("description", this.description);
            formData.append("advertisement", this.advertisement);
            const response = await fetch(`http://127.0.0.1:5000/category/${category_id}`, {
                method: "PUT",
                headers: {
                    "Authorization": "Bearer " + localStorage.getItem("access_token")
                },
                body: formData
            })
            const data = await response.json();
            if (!response.ok) {
                alert(data.error);
            }
            else {
                alert(data.message);
                this.$router.push("/all-categories");
            }
        },
        async getCategory(category_id) {
        const response = await fetch(`http://127.0.0.1:5000/category/${category_id}`, {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("access_token")
            }
        })
        const data = await response.json();
        if (!response.ok) {
            alert(data.error);
        }
        else {
            this.name = data.name;
            this.description = data.description;
        }
    }

    },
    

}
</script>