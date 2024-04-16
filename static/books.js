const $bookSearchButton = $('.book-search-button');
const $title = $('#title');
const $author = $('#author');
const $ISBN = $('#ISBN');
const $apiSearchResults = $('.api-search-results')

//book search click event handler
$bookSearchButton.on('click', async function(event) {
    console.log('search button pressed')
    event.preventDefault();
    $apiSearchResults.empty();
    let title = $title.val();
    let author = $author.val();
    let isbn = $ISBN.val();
    let response = await searchGoogleBooks(title, author, isbn);
    displaySearchResults(response);
})

//send book search query to GoogleBooks
async function searchGoogleBooks(title, author, isbn){
    title = title.replace(/ /g, '%20')
    author = author.replace(/ /g, '%20');
    let url = `https://www.googleapis.com/books/v1/volumes?q=intitle%3A%22${title}%22&inauthor%3A%22${author}%22&isbn%3A${isbn}`;
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