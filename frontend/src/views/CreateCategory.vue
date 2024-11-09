<template>
    <NavBar />
    <div class ="container mt-5">
        <h2>Create Category Here</h2>
        <form @submit.prevent="createCategory">
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
                <input type="file" class="form-control" id="advertisement" @change="handlefileChange">
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
export default{
    name: "CreateCategory",
    components: {
        NavBar
    },
    data(){
        return{
            name: "",
            description: "",
            advertisement: null
        }
    },
    methods:{
        handlefileChange(event){
            console.log("File changed")
            console.log(event)
            this.advertisement = event.target.files[0];
},

        async createCategory(){
            const formData = new FormData();
            formData.append("name", this.name);
            formData.append("description", this.description);
            formData.append("advertisement", this.advertisement);
            const response = await fetch("http://127.0.0.1:5000/category", {
                method: "POST",
                headers: {
                    "Authorization": "Bearer " + localStorage.getItem("access_token")
                },
                body: formData
            })
            const data = await response.json();
            if(!response.ok){
                alert(data.error);
            }
            else{
                alert(data.message);
                this.$router.push("/all-categories");
            }
        }

    }
}
</script>