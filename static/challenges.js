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
    currentURL = window.location.href
    if (currentURL.includes('user')){
        mainChallengesList = await ChallengeList.getYourChallenges();
    }
    else {
        mainChallengesList = await ChallengeList.getChallenges();
    }
    console.log(mainChallengesList);
    displayChallenges(mainChallengesList);
}

//display an instance of UserBookList on the page
function displayChallenges(array){
    console.log('begin displayChallenges')
    console.log(array);
    $challengesList.empty();
    currentURL = window.location.href
    for (let item of array){
        console.log(item);
        let $challengeTr = $('<tr></tr>');
        if (!currentURL.includes('user') && user_id == item.creator_id){
            let $name = $(`<td data-sortvalue="${item.name}"><a href="/challenges/${item.id}">${item.name}</a></td>`);
            $challengeTr.append($name);
        }
        else if (currentURL.includes('user')){
            let $name = $(`<td data-sortvalue="${item.name}"><a href="/users/${user_id}/challenges/${item.id}">${item.name}</a></td>`);
            $challengeTr.append($name);
        }
        else {
            let $name = $(`<td data-sortvalue="${item.name}">${item.name}</td>`);
            $challengeTr.append($name);
        }
        let $num_books = $(`<td>${item.num_books}</td>`);
        let $description = $(`<td>${item.description}</td>`);
        $challengeTr.append($num_books);
        $challengeTr.append($description);
        if (!currentURL.includes('user')){
            let $joinButton = $(`<td><form method="POST" action="/challenges/join/${item.id}"><button class="btn btn-primary">Join Challenge</button></form></td>`);
            $challengeTr.append($joinButton);
        }
        if (currentURL.includes('user')){
            let $start_date = $(`<td>${item.start_date}</td>`);
            if (item.end_date = ''){
                var $end_date = $('<td></td>')
            }
            else{
                var $end_date = $(`<td>${item.end_date}</td>`);
            }
            let $leaveButton = $(`<td><form method="POST" action="/challenges/leave/${item.id}"><button class="btn btn-danger">Leave Challenge</button></form></td>`);
            $challengeTr.append($start_date);
            $challengeTr.append($end_date);
            $challengeTr.append($leaveButton);
        }
        $challengesList.append($challengeTr);
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
        inputStyle: '',
        inputPlaceholder: "Search...",
        globalSearch: true,
        globalSearchExcludeColumns: [0],
        exactMatch: "auto"
    })
}

