class UserBook{

    constructor({id, user_id, book_id, title, authors, publisher, pub_date, pages, cover}){
        this.id = id
        this.title = title
        this.authors = authors
        this.publisher = publisher
        this.pub_date = pub_date
        this.pages = pages
        this.cover = cover
    }
}

class UserBookList {

    constructor(userBooks){
        this.userBooks = userBooks
    }

    //pulls full list of userbooks from the api and returns them as a new instance of UserBookList

    static async getUserBooks(user_id, list_type) {
        try{
            const response = await axios.get(`/api/${user_id}/lists/${list_type}`);
            return response.data;
        } catch (error) {
            alert('Something went wrong. Please try again.')
        }
    }
}

class Challenge{

    constructor({id, name, num_books, description}){
        this.id = id
        this.name = name
        this.num_books = num_books
        this.description = description
    }
}

class ChallengeList {

    constructor(challenges){
        this.challenges = challenges
    }

    //pulls list of all challenges and returns them as a new instance of ChallengeList
    static async getChallenges(){
        try{
            const response = await axios.get('/api/challenges');
            return response.data;
        } catch (error) {
            alert('Something went wrong. Please try again.')
        }
    }

    //pulls list of challenges the user has joined and returns them as a new instance of ChallengeList
    static async getYourChallenges(){
        try{
            const response = await axios.get('/api/yourchallenges')
            return response.data
        } catch (error){
            alert('Something went wrong. Please try again.')
        }
    }
}