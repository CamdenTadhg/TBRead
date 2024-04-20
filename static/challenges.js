const { default: axios } = require("axios");

const $challengeList = $('.challenge-list');
const $table = $('.challenges-table');
const $addCategoryButton = $('.add-category-button');
const $removeCategoryButton = $('.remove-category-button');
const $categoryNameField = $('.category-name-field');
const $categoryDescriptionField = $('.category-description-field')
const $categoryIdsField = $('#category-ids-field');
const $suggestions = $('.suggestions');
const categories = categories;
const $errorSpan = $('.error-span');
const $categoryForm = $('.category-form')

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

//event handler for typing in category name field
$categoryNameField.on('keyup', searchHandler);
//event handler for selection of category name
$suggestions.on('click', async function(){
    useSuggestion();
});

//searchHandler function for autocomplete category name field
function searchHandler(){
    $suggestions.html('');
    searchString = $categoryNameField.val();
    if (searchString !== ''){
        showSuggestions(search(searchString))
    }
}

function search(str){
    let results = [];
    for (let category of categories){
        if (category.toLowerCase().includes(str.toLowerCase())){
            results.push(category);
        }
    }
    sortResults(results, str)
    return results;
}

//simple function to make categories that begin with the search string appear first
function sortResults(results, str){
    for (let i=0; i < results.length; i++){
        let index = results[i].toLowerCase().indexOf(str.toLowerCase())
        let counter = 0
        if (index === 0){
            results.splice(counter, 0, results[i]);
            results.splice(i+1, 1);
            counter++;
        }
    }
    return results;
}

//display suggestions and highlights text which matches the search string
function showSuggestions(results){
    for (let result of results){
        const $resultLi = $('<li></li>')
        let searchStr = input.value.toLowerCase();
        let regex = new RegExp('(' + searchStr + ')', 'gi');
        $resultLi.html = result.replace(regex, '<b>$1</b>');
        $suggestions.append(resultLi);
    }
}

//populate the name field with the suggestion and the description field with the appropriate description
async function useSuggestion(event){
    $categoryNameField.val() = event.target.innerText;
    $suggestions.html = '';
    data = {name: $categoryNameField.val()}
    const response = await axios.get('/api/category/description', data)
}

//on add category button press, send information via axios to server
$addCategoryButton.on('click', async function(event){
    event.preventDefault();
    $categoryForm.find('.error-span').remove();
    console.log('add category button pressed');
    if ($categoryNameField.val() = ''){
        $errorSpan = $('<span class="text-sm text-danger error-span">Please enter a category name</span>')
        $categoryForm.append($errorSpan);
    } else {
        newCategory = gatherCategoryData();
        newCategoryId = await newCategory.addCategory();
        addToCategoryIds(newCategoryId);
        updateForm()
    }
})

//gather data from form and create new instance of category
function gatherCategoryData(){
    console.log('starting gatherCategoryData');
    const name = $categoryNameField.val();
    const description = $categoryDescriptionField.val();
    categoryData = {name: name, description: description};
    const newCategory = new Category(categoryData);
    console.log(newCategory);
    return newCategory;
}

//add new category's id to the hidden category id field's value.
function addToCategoryIds(categoryId){}

//update complete form to be inactive and add new active form.
function updateForm(){}