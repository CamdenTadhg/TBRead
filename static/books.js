let $bookSearchButton = $('.book-search-button');
let $field = $('#field');
let $term = $('#term');
let $apiSearchResults = $('.api-search-results');
let $assignChallengeButton = $('.assign-challenge-button');
let $challengesField = $('#challenges');
let $assignToChallengeForm = $('.assign-to-challenge-form');
let $removeChallengeButton = $('.remove-challenge-button');
let $coverColumn = $('#cover');

//disables sort feature on cover column
$coverColumn.click(function(event) {
    event.preventDefault();
    return false;
});

//book search click event handler
$bookSearchButton.on('click', async function(event) {
    event.preventDefault();
    $apiSearchResults.empty();
    let field = $field.val();
    let term = $term.val();
    let response = await searchGoogleBooks(field, term);
    displaySearchResults(response);
});

//send book search query to GoogleBooks
async function searchGoogleBooks(field, term){
    let url;
    if (field === 'isbn'){
        url = `https://www.googleapis.com/books/v1/volumes?q=isbn:${term}`
    }
    else if (field === 'title'){
        term = term.replace(/ /g, '%20')
        url = `https://www.googleapis.com/books/v1/volumes?q=intitle%3A%22${term}%22`
    } else {
        term = term.replace(/ /g, '%20');
        url = `https://www.googleapis.com/books/v1/volumes?q=inauthor%3A%22${term}%22`;
    }
    let response = await axios.get(url)
    return response.data.items;
}

//display book search results
function displaySearchResults(response){
    const index = Math.min(response.length - 1, 14);
    let $cover, $displayTitle, $displayAuthor, $publication;
    for (let i = 0; i <= index; i++){
        let $bookDiv = $(`<div class="row my-1"></div>`);
        if (response[i].volumeInfo.imageLinks){
            $cover = $(`<div class="col-2"><img src="${response[i].volumeInfo.imageLinks.smallThumbnail}"></div>`);
        } else {
            $cover = $('<div class="col-2"></div>');
        }
        $textDiv = $('<div class="col"></div>');
        if (response[i].volumeInfo.subtitle){
            $displayTitle = $(`<div><a href="/books/${response[i].id}">${response[i].volumeInfo.title}: ${response[i].volumeInfo.subtitle}</a></div>`);
        } else {
           $displayTitle = $(`<div><a href="/books/${response[i].id}">${response[i].volumeInfo.title}</a></div>`)
        }
        if (response[i].volumeInfo.authors){
            $displayAuthor = $(`<div>${response[i].volumeInfo.authors[0]}</div>`);
        }
        if (response[i].volumeInfo.publisher && response[i].volumeInfo.publishedDate){
            $publication = $(`<div>${response[i].volumeInfo.publisher}, ${response[i].volumeInfo.publishedDate}</div>`);
        } else if (response[i].volumeInfo.publisher){
            $publication = $(`<div>${response[i].volumeInfo.publisher}</div>`);
        } else if (response[i].volumeInfo.publishedDate) {
            $publication = $(`<div>${response[i].volumeInfo.publishedDate}</div>`);
        }
        $textDiv.append($displayTitle);
        $textDiv.append($displayAuthor);
        $textDiv.append($publication);
        $bookDiv.append($cover);
        $bookDiv.append($textDiv)
        $apiSearchResults.append($bookDiv);
    }
}

//assign a book as part of a challenge
$assignChallengeButton.on('click', async function(event){
    event.preventDefault();
    $assignToChallengeForm.find('.error-span').remove();
    //get the challenge being assigned to
    const challenge_id = $challengesField.val();
    //get the userbook_id
    currentURL = window.location.href;
    const userbook_id = parseInt(currentURL.substring(currentURL.lastIndexOf('/') + 1));
    //send the data
    const data = {'challenge_id': challenge_id};
    const response = await axios.post(`/api/users_books/${userbook_id}/assign`, data);
    //handle response
    if (response.data['success']){
        $errorSpan = $('<span class="text-sm text-success error-span">Book assigned to challenge</span>');
        $assignToChallengeForm.append($errorSpan);
    }
    if (response.data['error']){
        $errorSpan = $('<span class="text-sm text-danger error-span">This book is already assigned to this challenge.</span>');
        $assignToChallengeForm.append($errorSpan);
    }
});

//remove a book as part of a challenge
$removeChallengeButton.on('click', async function(event){
    event.preventDefault();
    $assignToChallengeForm.find('.error-span').remove();
    //get the challenge being removed from 
    const challenge_id = $challengesField.val();
    currentURL = window.location.href;
    //get the userbook id
    const userbook_id = parseInt(currentURL.substring(currentURL.lastIndexOf('/') + 1));
    //send the data to the API
    const data = {'challenge_id': challenge_id};
    const response = await axios.post(`/api/users_books/${userbook_id}/remove`, data);
    //handle response
    if (response.data['success']){
        $errorSpan = $('<span class="text-sm text-success error-span">Book removed from challenge</span>');
        $assignToChallengeForm.append($errorSpan);
    }
    if (response.data['error']){
        $errorSpan = $('<span class="text-sm text-danger error-span">This book is not assigned to this challenge</span>')
        $assignToChallengeForm.append($errorSpan);
    }
});