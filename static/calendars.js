const options = {
    dayNames: ["Sun", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat"]
}

//display calendar
const today = moment().format('YYYY-MM-DD');
let calendar = $('#calendar').calendarGC(options);
calendar.setDate(today);

//on page load, populate calendar
$(document).ready(function(){
    console.log('page load event handler started');
    getPostDates()
});




