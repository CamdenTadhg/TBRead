const $bookSearchButton = $('.book-search-button');
const $field = $('#field');
const $term = $('#term');
const $apiSearchResults = $('.api-search-results');
const $assignChallengeButton = $('.assign-challenge-button');
const $challengesField = $('#challenges');
const $assignToChallengeForm = $('.assign-to-challenge-form');
const $removeChallengeButton = $('.remove-challenge-button');

//book search click event handler
$bookSearchButton.on('click', async function(event) {
    console.log('search button pressed')
    event.preventDefault();
    $apiSearchResults.empty();
    let field = $field.val();
    let term = $term.val();
    let response = await searchGoogleBooks(field, term);
    displaySearchResults(response);
})

//send book search query to GoogleBooks
async function searchGoogleBooks(field, term){
    if (field === 'isbn'){
        var url = `https://www.googleapis.com/books/v1/volumes?q=isbn:${term}`
    }
    else if (field === 'title'){
        term = term.replace(/ /g, '%20')
        var url = `https://www.googleapis.com/books/v1/volumes?q=intitle%3A%22${term}%22`
    } else {
        term = term.replace(/ /g, '%20');
        var url = `https://www.googleapis.com/books/v1/volumes?q=inauthor%3A%22${term}%22`;
    }
    console.log(url);
    let response = await axios.get(url)
    console.log(response);
    return response.data.items;
}

//display book search results
function displaySearchResults(response){
    for (let i = 0; i <= 9; i++){
        let $bookDiv = $(`<div class="row border"></div>`);
        if (response[i].volumeInfo.imageLinks){
            var $cover = $(`<div class="col-4"><img src="${response[i].volumeInfo.imageLinks.smallThumbnail}"></div>`);
        } else {
            var $cover = $('<div class="col-4"></div>');
        }
        $textDiv = $('<div class="col"></div>');
        if (response[i].volumeInfo.subtitle){
            var $displayTitle = $(`<div><a href="/books/${response[i].id}">${response[i].volumeInfo.title}: ${response[i].volumeInfo.subtitle}</a></div>`);
        } else {
           var $displayTitle = $(`<div><a href="/books/${response[i].id}">${response[i].volumeInfo.title}</a></div>`)
        }
        if (response[i].volumeInfo.authors){
            var $displayAuthor = $(`<div>${response[i].volumeInfo.authors[0]}</div>`);
        }
        if (response[i].volumeInfo.publisher){
            var $publication = $(`<div>${response[i].volumeInfo.publisher}, ${response[i].volumeInfo.publishedDate}</div>`);
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
    console.log('starting assign challenge');
    $assignToChallengeForm.find('.error-span').remove();
    console.log($challengesField.val());
    //get the challenge being assigned to
    const challenge_id = $challengesField.val();
    //get the userbook_id
    currentURL = window.location.href;
    const userbook_id = parseInt(currentURL.substring(currentURL.lastIndexOf('/') + 1));
    console.log('userbook_id:', userbook_id);
    //send the data
    const data = {'challenge_id': challenge_id};
    const response = await axios.post(`/api/users_books/${userbook_id}/assign`, data);
    console.log(response);
    if (response.data['success']){
        console.log('success response');
        $errorSpan = $('<span class="text-sm text-success error-span">Book assigned to challenge</span>');
        $assignToChallengeForm.append($errorSpan);
    }
    if (response.data['error']){
        console.log('error response');
        $errorSpan = $('<span class="text-sm text-danger error-span">This book is already assigned to this challenge.</span>');
        $assignToChallengeForm.append($errorSpan);
    }
})

//remove a book as part of a challenge
$removeChallengeButton.on('click', async function(event){
    event.preventDefault();
    console.log('starting remove challenge');
    $assignToChallengeForm.find('.error-span').remove();
    console.log($challengesField.val());
    const challenge_id = $challengesField.val();
    currentURL = window.location.href;
    const userbook_id = currentURL[currentURL.length-1];
    const data = {'challenge_id': challenge_id};
    const response = await axios.post(`/api/users_books/${userbook_id}/remove`, data);
    console.log(response);
    if (response.data['success']){
        console.log('success response');
        $errorSpan = $('<span class="text-sm text-success error-span">Book removed from challenge</span>');
        $assignToChallengeForm.append($errorSpan);
    }
    if (response.data['error']){
        console.log('error response');
        $errorSpan = $('<span class="text-sm text-danger error-span">This book is not assigned to this challenge</span>')
        $assignToChallengeForm.append($errorSpan);
    }
})