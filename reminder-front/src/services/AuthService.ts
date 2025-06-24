import $api from "../http";



export default class AuthService {
    static async login(usernameOrEmail: string, password: string) {
        const formData = new FormData();
        console.log(usernameOrEmail, password)
        formData.append('username', usernameOrEmail);
        formData.append('password', password);

        return $api.post(
            '/auth/token',
            formData,
            {
                headers: {"Content-Type": "multipart/form-data"}
            })
    }

    static async refresh() {
        return $api.get('/auth/refresh')
    }

    static async getme() {
        return $api.get('/auth/getme')
    }
}