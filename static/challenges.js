let $challengesList = $('.challenge-list');
let $table = $('.challenges-table');
let $allTab = $('.all-tab');
let $yourTab = $('.your-tab');


//on page load, display all challenges
$(document).ready(function(){
    activeTab();
    challengesOnStart();
});

//initial function to show challenge list on site load
async function challengesOnStart(){
    currentURL = window.location.href
    if (currentURL.includes('user')){
        mainChallengesList = await ChallengeList.getYourChallenges();
    }
    else {
        mainChallengesList = await ChallengeList.getChallenges();
    }
    displayChallenges(mainChallengesList);
}

//display an instance of ChallengeList on the page
function displayChallenges(array){
    $challengesList.empty();
    currentURL = getCurrentURL();
    for (let item of array){
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
            let $joinButton = $(`<td><form method="POST" action="/challenges/join/${item.id}"><button class="btn btn-primary join">Join Challenge</button></form></td>`);
            $challengeTr.append($joinButton);
        }
        if (currentURL.includes('user')){
            if (item.start_date === undefined){
                var $start_date = $('<td></td>')
            }
            else {
                var $start_date = $(`<td>${item.start_date}</td>`);
            }
            if (item.end_date === undefined){
                var $end_date = $('<td></td>')
            }
            else{
                var $end_date = $(`<td>${item.end_date}</td>`);
            }
            let $leaveButton = $(`<td><form method="POST" action="/challenges/leave/${item.id}"><button class="btn btn-danger leave ">Leave Challenge</button></form></td>`);
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

function activeTab(){
    currentURL = getCurrentURL();
    console.log('$yourTab = ', $yourTab);
    console.log('$allTab = ', $allTab);
    let currentList, inactiveList;
    currentURL.includes('users') ? currentList = $yourTab : currentList = $allTab
    currentList === $allTab ? inactiveList = $yourTab : inactiveList = $allTab
    let currentListClassList = currentList.attr('class');
    console.log('currentListClassList = ', currentListClassList);
    let inactiveListClassList = inactiveList.attr('class');
    console.log('inactiveListClassList = ', inactiveListClassList);
    if (currentListClassList.includes('btn-secondary')){
        currentList.removeClass('btn-secondary');
        currentList.addClass('btn-primary');
    }
    inactiveListClassList = inactiveList.attr('class');
    if (inactiveListClassList.includes('btn-primary')){
        inactiveList.removeClass('btn-primary');
        inactiveList.addClass('btn-secondary');
    }
}

//allows mocking the url for testing purposes
function getCurrentURL() {
    return window.location.href;
}
