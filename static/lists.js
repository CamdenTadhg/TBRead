$userBookList = $('.user-book-list');
$table = $('.book-list-table');

//on page load, display contents of list
$(document).ready(function(){
    console.log('event handler started')
    userBooksOnStart();
});

//initial function to show book list on site load
async function userBooksOnStart(){
    console.log('begin userBooksOnStart')
    console.log(type);
    mainUserBooksList = await UserBookList.getUserBooks(g_user_id, type);
    console.log(mainUserBooksList);
    displayUserBooks(mainUserBooksList);
}

//display an instance of UserBookList on the page
function displayUserBooks(array){
    console.log('begin displayUserBooks')
    console.log(array);
    $userBookList.empty();
    currentURL = window.location.href;
    console.log(currentURL);
    for (let book of array){
        let $bookTr = $('<tr></tr>');
        let $cover = $(`<td><img class="list-cover" src=${book.cover}></td>`);
        let $title = $(`<td data-sortvalue="${book.title}"><a href="/users_books/${book.id}">${book.title}</a></td>`);
        let $author = $(`<td>${book.author}</td>`);
        let $publisher = $(`<td>${book.publisher}</td>`);
        let $pub_date = $(`<td>${book.pub_date}</td>`)
        let $pages = $(`<td>${book.pages}</td>`)
        let $delete = $(`<td><form method="POST" action="/users_books/${book.id}/delete"><button class="btn btn-danger"><i class="fa-solid fa-trash-can"></i></button></form></td>`)
        $bookTr.append($cover);
        $bookTr.append($title);
        $bookTr.append($author);
        $bookTr.append($publisher);
        $bookTr.append($pub_date);
        $bookTr.append($pages);
        $bookTr.append($delete)
        if (!currentURL.includes('dnf')){
            let $DNF = $(`<td><form method="POST" action="/users_books/${book.id}/transfer/DNF"><button class="btn btn-info">DNF</button></form></td>`);
            $bookTr.append($DNF);
        }
        if (!currentURL.includes('complete')){
            let $complete = $(`<td><form method="POST" action="/users_books/${book.id}/transfer/Complete"><button class="btn btn-info">Complete</button></form></td>`);
            $bookTr.append($complete);
        }
        if (!currentURL.includes('/tbr')){
            let $TBR = $(`<td><form method="POST" action="/users_books/${book.id}/transfer/TBR"><button class="btn btn-info">TBR</button></form></td>`);
            $bookTr.append($TBR);
        }
        $userBookList.append($bookTr);
    }
    //table sorting and searching plugin
    $table.fancyTable({
        sortColumn: 1,
        sortOrder: 'asc',
        sortable: true,
        localeCompare: true,
        pagination: true, 
        paginationClass: 'btn btn-primary',
        perPage: 25,
        inputStyle: '',
        inputPlaceholder: "Search...",
        globalSearch: true,
        globalSearchExcludeColumns: [0],
        exactMatch: "auto"
    })
}





