export default {
    data() {
        return {
            user: null,
            role: null,
            isLoggedIn: false
        }
    },
    async created() {
        await this.checkAuth();
    },
    methods: {
        async checkAuth() {
            console.log("Checking Authorization")
            const access_token = localStorage.getItem("access_token");
            if (!access_token) {
                this.isLoggedIn = false;
                this.user = null;
                this.role = null;
            }
            else {
                try {
                    this.user = await this.getUserDetails(access_token);
                    console.log(this.user);
                } catch (error) {
                    console.log(error)
                }
            }

        },
        async getUserDetails(access_token) {
            const response = await fetch("http://127.0.0.1:5000/get-user-info", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + access_token
                }
            })
            const data = await response.json()
            if (!response.ok) {
                this.isLoggedIn = false;
                this.role = null;
                console.log("Something wrong happened!");
                return null;
            } else {
                this.role = data.user.role;
                this.isLoggedIn = true;
                return data.user;
            }

        },
        async logout(){
            const response = await fetch("http://127.0.0.1:5000/logout", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + localStorage.getItem("access_token")
                }
            })
            const data = response.json()
            if (!response.ok){
                console.log("Something wrong happened!")
            }
            else{
                this.user = null;
                this.role = null;
                this.isLoggedIn = false;
                localStorage.removeItem("access_token")
                this.$router.push("/login")
            }
            
        }
    }
}