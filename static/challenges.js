$challengeList = $('.challenge-list');
$table = $('.challenges-table');

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
    for (let challenge of array){
        let $challengeTr = $('<tr></tr>');
        let $name = $(`<td data-sortvalue="${challenge.name}"><a href="/challenges/${challenge.id}">${challenge.name}</a></td>`);
        let $num_books = $(`<td>${challenge.num_books}</td>`);
        let $description = $(`<td>${challenge.description}</td>`);
        $challengeTr.append($name);
        $challengeTr.append($num_books);
        $challengeTr.append($description);
        $challengeList.append($challengeTr);
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