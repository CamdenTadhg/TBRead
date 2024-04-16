$bookSearchButton = $('.book-search-button');
$title = $('#title');
$author = $('#author');
$ISBN = $('#ISBN');
$apiSearchResults = $('.api-search-results')

//book search click event handler
$bookSearchButton.on('click', async function(event) {
    event.preventDefault();
    title = $title.val();
    author = $author.val();
    isbn = $ISBN.val();
    response = await searchGoogleBooks(title, author, isbn);
    displaySearchResults(response);
})

//send book search query to GoogleBooks
async function searchGoogleBooks(title, author, isbn){
    title = title.replace(/ /g, '%20')
    author = author.replace(/ /g, '%20');
    url = `https://www.googleapis.com/books/v1/volumes?q=intitle%3A%22${title}%22&inauthor%3A%22${author}%22&isbn%3A${isbn}`;
    response = await axios.get(url)
    return response.data.items;
}

//display book search results
function displaySearchResults(response){
    for (let i = 0; i <= 9; i++){
        console.log(response[i].id);
        $bookDiv = $(`<div class="row border"></div>`);
        if (response[i].volumeInfo.imageLinks){
            $cover = $(`<div class="col-4"><img src="${response[i].volumeInfo.imageLinks.smallThumbnail}"></div>`);
        } else {
            $cover = $('<div class="col-4"></div>');
        }
        $textDiv = $('<div class="col"></div>');
        if (response[i].volumeInfo.subtitle){
            $title = $(`<div><a href="/books/${response[i].id}">${response[i].volumeInfo.title}: ${response[i].volumeInfo.subtitle}</a></div>`);
        } else {
            $title = $(`<div><a href="/books/${response[i].id}">${response[i].volumeInfo.title}</a></div>`)
        }
        $author = $(`<div>${response[i].volumeInfo.authors[0]}</div>`);
        $publication = $(`<div>${response[i].volumeInfo.publisher}, ${response[i].volumeInfo.publishedDate}</div>`);
        $textDiv.append($title);
        $textDiv.append($author);
        $textDiv.append($publication);
        $bookDiv.append($cover);
        $bookDiv.append($textDiv)
        $apiSearchResults.append($bookDiv);
    }
}