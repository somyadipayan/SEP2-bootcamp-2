<template>
    <NavBar/>
    <div class="container mt-5">
    <h2>Login Here</h2>
    <form @submit.prevent="login">
      <div class="mb-3">
        <label for="email" class="form-label">Email address</label>
        <input v-model="email" type="email" class="form-control" id="email">
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input  v-model="password" type="password" class="form-control" id="password">
      </div>
      <button type="submit" class="btn btn-primary">Submit</button>
    </form>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
export default{
    data() {
        return {
            email: '',
            password: '',
        }
    },
    components:{
        NavBar
    },
    methods:{

        async login(){
            try{
                const response = await fetch("http://127.0.0.1:5000/login", {
                method: "POST",
                headers:{
                    "Content-Type": "application/json"
                },
                body:JSON.stringify({ 
                    email: this.email,
                    password: this.password,
                })
            })
            const data = await response.json()
            if(!response.ok){
                alert(data.error)
            }
            else{
                localStorage.setItem("access_token", data.access_token)
                alert(data.message)
                // Push/Redirect to HomePage
                this.$router.push('/')
            }
            }
            catch(error){
                console.log(error)
            }
        }
    }
}
</script>