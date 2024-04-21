const $challengesList = $('.challenge-list');
const $table = $('.challenges-table');


//on page load, display all challenges
$(document).ready(function(){
    console.log('event handler started')
    challengesOnStart();
});

//initial function to show challenge list on site load
async function challengesOnStart(){
    console.log('begin challengesOnStart')
    mainChallengesList = await ChallengeList.getChallenges();
    console.log(mainChallengesList);
    displayChallenges(mainChallengesList);
}

//display an instance of UserBookList on the page
function displayChallenges(array){
    console.log('begin displayChallenges')
    console.log(array);
    $challengesList.empty();
    for (let item of array){
        console.log(item);
        let $challengeTr = $('<tr></tr>');
        let $name = $(`<td data-sortvalue="${item.name}"><a href="/challenges/${item.id}">${item.name}</a></td>`);
        let $num_books = $(`<td>${item.num_books}</td>`);
        let $description = $(`<td>${item.description}</td>`);
        $challengeTr.append($name);
        $challengeTr.append($num_books);
        $challengeTr.append($description);
        $challengesList.append($challengeTr);
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

