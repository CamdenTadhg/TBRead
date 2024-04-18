$userBookList = $('.user-book-list');
$table = $('.book-list-table');

//on page load, display contents of list
$(document).ready(function(){
    console.log('event handler started')
    userBooksOnStart();
    //table sorting and searching plugin
    $table.fancyTable({
        sortColumn: 1,
        sortOrder: 'asc',
        sortable: true,
        pagination: true, 
        paginationClass: 'btn btn-primary',
        perPage: 25,
        inputStyle: '',
        inputPlaceholder: "Search...",
        globalSearch: true,
        globalSearchExcludeColumns: [0],
        exactMatch: "auto"
    })
});

//initial function to show book list on site load
async function userBooksOnStart(){
    console.log('begin userBooksOnStart')
    mainUserBooksList = await UserBookList.getUserBooks(g_user_id, type);
    console.log(mainUserBooksList);
    displayUserBooks(mainUserBooksList);
}

//display an instance of UserBookList on the page
function displayUserBooks(array){
    console.log('begin displayUserBooks')
    console.log(array);
    $userBookList.empty();
    for (let book of array){
        let $bookTr = $('<tr></tr>');
        let $cover = $(`<td><img class="list-cover" src=${book.cover}></td>`);
        let $title = $(`<td><a href="/books/${book.id}">${book.title}</a></td>`);
        let $author = $(`<td>${book.author}</td>`);
        let $publisher = $(`<td>${book.publisher}</td>`);
        let $pub_date = $(`<td>${book.pub_date}</td>`)
        let $pages = $(`<td>${book.pages}</td>`)
        $bookTr.append($cover);
        $bookTr.append($title);
        $bookTr.append($author);
        $bookTr.append($publisher);
        $bookTr.append($pub_date);
        $bookTr.append($pages);
        $userBookList.append($bookTr);
    }
}



