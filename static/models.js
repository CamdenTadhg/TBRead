const { default: axios } = require("axios")

class UserBook{

    constructor({id, user_id, book_id, title, authors, publisher, pub_date, description, isbn, page_count, age_category, thumbnail, notes, script}){
        this.id = id
        this.user_id = user_id
        this.book_id = book_id
        this.title = title
        this.authors = authors
        this.publisher = publisher
        this.pub_date = pub_date
        this.description = description
        this.isbn = isbn
        this.page_count = page_count
        this.age_category = age_category
        this.thumbnail = thumbnail
        this.notes = notes
        this.script = script
    }
}

class UserBookList {

    constructor(userBooks){
        this.user_id = user_id
        this.userBooks = userBooks
    }

    //pulls full list of books from the api and returns them as a new instance of UserBookList

    static async getUserBooks(user_id, list_type) {
        try{
            console.log('starting getUserBooks');
            const response = await axios.get(`/api/${user_id}/lists/${list_type}`);
            console.log(response);
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
            console.log('starting getChallenges');
            const response = await axios.get('/api/challenges');
            console.log(response);
            return response.data;
        } catch (error) {
            alert('Something went wrong. Please try again.')
        }
    }
}

class Category{

    constructor({name, description}){
        this.name = name
        this.description = description
    }

    async addCategory(){
        try{
            console.log('starting add category');
            const response = await axios.post('/api/category');
            console.log(response);
            return response.data.id;
        } catch (error){
            alert('Add category form submission failed. Please try again.')
        }
    }
}