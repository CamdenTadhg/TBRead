let $userBookList = $('.user-book-list');
let $table = $('.book-list-table');
let $tbrTab = $('.tbr-tab');
let $dnfTab = $('.dnf-tab');
let $completeTab = $('.complete-tab');

//on page load, display welcome message and contents of list
$(document).ready(function(){
    activeTab();
    userBooksOnStart();
});

//initial function to show book list on site load
async function userBooksOnStart(){
    mainUserBooksList = await UserBookList.getUserBooks(g_user_id, type);
    displayUserBooks(mainUserBooksList);
}

//display an instance of UserBookList on the page
function displayUserBooks(array){
    $userBookList.empty();
    currentURL = getCurrentURL();
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
        $bookTr.append($delete);
        //if not on DNF list, display button to transfer book to DNF list. 
        if (!currentURL.includes('dnf')){
            let $DNF = $(`<td><form method="POST" action="/users_books/${book.id}/transfer/DNF"><button class="btn-responsive btn-info transfer">Move to DNF</button></form></td>`);
            $bookTr.append($DNF);
        }
        //if not on Complete list, display button to transfer book to Complete list. 
        if (!currentURL.includes('complete')){
            let $complete = $(`<td><form method="POST" action="/users_books/${book.id}/transfer/Complete"><button class="btn-responsive btn-info transfer">Move to Complete</button></form></td>`);
            $bookTr.append($complete);
        }
        //if not on TBR list, display button to transfer book to TBR list
        if (!currentURL.includes('lists/tbr')){
            let $TBR = $(`<td><form method="POST" action="/users_books/${book.id}/transfer/TBR"><button class="btn-responsive btn-info transfer">Move to TBR</button></form></td>`);
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
        inputStyle: 'border: 1px solid silver',
        inputPlaceholder: "Search...",
        globalSearch: true,
        globalSearchExcludeColumns: [0],
        exactMatch: "auto"
    });
}

//function to highlight the active tab in tab display
function activeTab(){
    let currentURL = getCurrentURL();
    const currentListName = `$${currentURL.substring(currentURL.lastIndexOf('/') + 1)}Tab`;
    const currentList = eval(currentListName);
    listArray = [$tbrTab, $dnfTab, $completeTab]
    tempListArray = listArray.filter((list) => list != currentList);
    currentListClassList = currentList.attr('class');
    console.log('currentListClassList is ', currentListClassList);
    if (currentListClassList.includes('btn-secondary')){
        currentList.removeClass('btn-secondary');
        currentList.addClass('btn-primary');
    }
    for (let list of tempListArray){
        let listClassList = list.attr('class');
        if (listClassList.includes('btn-primary')){
            list.removeClass('btn-primary');
            list.addClass('btn-secondary');
        }
    }
}

//allows mocking the url for testing purposes
function getCurrentURL() {
    return window.location.href;
}





