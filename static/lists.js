let $userBookList = $('.user-book-list');
let $table = $('.book-list-table');
let $tbrTab = $('.tbr-tab');
let $dnfTab = $('.dnf-tab');
let $completeTab = $('.complete-tab');

//on page load, display welcome message and contents of list
$(document).ready(function(){
    userBooksOnStart();
    activeTab();
});

//initial function to show book list on site load
async function userBooksOnStart(){
    mainUserBooksList = await UserBookList.getUserBooks(g_user_id, type);
    displayUserBooks(mainUserBooksList);
}

//display an instance of UserBookList on the page
function displayUserBooks(array){
    $userBookList.empty();
    currentURL = window.location.href;
    for (let book of array){
        let $bookTr = $('<tr></tr>');
        let $cover = $(`<td><img class="list-cover" src=${book.cover}></td>`);
        let $title = $(`<td data-sortvalue="${book.title}"><a href="/users_books/${book.id}">${book.title}</a></td>`);
        let $author = $(`<td>${book.authors}</td>`);
        let $publisher = $(`<td>${book.publisher}</td>`);
        let $pub_date = $(`<td>${book.pub_date}</td>`)
        let $pages = $(`<td>${book.pages}</td>`)
        let $delete = $(`<td><form method="POST" action="/users_books/${book.id}/delete"><button class="btn btn-danger delete"><i class="fa-solid fa-trash-can"></i></button></form></td>`)
        $bookTr.append($cover);
        $bookTr.append($title);
        $bookTr.append($author);
        $bookTr.append($publisher);
        $bookTr.append($pub_date);
        $bookTr.append($pages);
        $bookTr.append($delete)
        if (!currentURL.includes('dnf')){
            let $DNF = $(`<td><form method="POST" action="/users_books/${book.id}/transfer/DNF"><button class="btn btn-info transfer">Move to DNF</button></form></td>`);
            $bookTr.append($DNF);
        }
        if (!currentURL.includes('complete')){
            let $complete = $(`<td><form method="POST" action="/users_books/${book.id}/transfer/Complete"><button class="btn btn-info transfer">Move to Complete</button></form></td>`);
            $bookTr.append($complete);
        }
        if (!currentURL.includes('lists/tbr')){
            let $TBR = $(`<td><form method="POST" action="/users_books/${book.id}/transfer/TBR"><button class="btn btn-info transfer">Move to TBR</button></form></td>`);
            $bookTr.append($TBR);
        }
        $userBookList.append($bookTr);
    }
    //table sorting and searching plugin
    $table.fancyTable({
        sortColumn: 0,
        sortOrder: 'asc',
        sortable: true,
        localeCompare: true,
        pagination: true, 
        paginationClass: 'btn btn-primary',
        perPage: 25,
        inputStyle: 'border: 1px solid silver',
        inputPlaceholder: "Search...",
        globalSearch: true,
        globalSearchExcludeColumns: [0],
        exactMatch: "auto"
    });
}

function activeTab(){
    currentURL = window.location.href;
    const currentList = eval(`$${currentURL.substring(currentURL.lastIndexOf('/') + 1)}Tab`);
    listArray = [$tbrTab, $dnfTab, $completeTab]
    tempListArray = listArray.filter((list) => list != currentList);
    currentListClassList = currentList.attr('class');
    if (currentListClassList.includes('btn-secondary')){
        currentList.removeClass('btn-secondary');
        currentList.addClass('btn-primary');
    }
    for (let list of tempListArray){
        listClassList = list.attr('class');
        if (listClassList.includes('btn-primary')){
            list.removeClass('btn-primary');
            list.addClass('btn-secondary');
        }
    }
}





