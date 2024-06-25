describe('book search event handler', () => {
    let searchGoogleBooksSpy, displaySearchResultsSpy;
    beforeEach(() => {
        //create spies
        searchGoogleBooksSpy = jasmine.createSpy('searchGoogleBooks');
        window.searchGoogleBooks = searchGoogleBooksSpy;
        displaySearchResultsSpy = jasmine.createSpy('displaySearchResults');
        window.displaySearchResults = displaySearchResultsSpy;

        //set up DOM
        $apiSearchResults = $('<div class="api-search-results">Search Results Here</div>').appendTo('body');
        $field = $('<input id="field">').appendTo('body');
        $term = $('<input type="text" id="term">').appendTo('body');
        $bookSearchButton = $('<button class="book-search-button">Search</button>')

        //attach event handler
        $bookSearchButton.on('click', async function(event) {
            event.preventDefault();
            $apiSearchResults.empty();
            let field = $field.val();
            let term = $term.val();
            let response = await searchGoogleBooks(field, term);
            displaySearchResults(response);
        });
    });

    afterEach(() => {
        //clean up DOM
        $apiSearchResults.remove();
        $field.remove();
        $term.remove();
        $bookSearchButton.remove();

        window.searchGoogleBooks = searchGoogleBooks;
        window.displaySearchResults = displaySearchResults;
    });

    it('calls the necessary functions to search Google Books', async () => {
        $field.val('title');
        $term.val('The Velveteen Rabbit');

        const event = $.Event('click');
        await $bookSearchButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect($apiSearchResults[0].innerText).toEqual('');
        expect(searchGoogleBooksSpy).toHaveBeenCalledWith('title', 'The Velveteen Rabbit');
        expect(displaySearchResultsSpy).toHaveBeenCalled();
    });
});

describe('searchGoogleBooks', () => {
    let axiosGetSpy
    beforeEach(() => {
        axiosGetSpy = spyOn(axios, 'get').and.returnValue(Promise.resolve({data: {items: [{title: 'Harry Potter'}, {title: 'Harry Potter 2'}]}}));
    });

    it('constructs and sends an appropriate isbn search', async () => {
        let response = await searchGoogleBooks('isbn', 9781452659487);

        expect(axiosGetSpy).toHaveBeenCalledWith('https://www.googleapis.com/books/v1/volumes?q=isbn:9781452659487');
        expect(response).toEqual([{title: 'Harry Potter'}, {title: 'Harry Potter 2'}]);
    });

    it('constructs and sends an appropriate title search', async () => {
        let response = await searchGoogleBooks('title', 'The Velvet Pumpernickel');

        expect(axiosGetSpy).toHaveBeenCalledWith('https://www.googleapis.com/books/v1/volumes?q=intitle%3A%22The%20Velvet%20Pumpernickel%22');
        expect(response).toEqual([{title: 'Harry Potter'}, {title: 'Harry Potter 2'}]);
    });

    it('constructs and sends an appropriate author search', async () => {
        let response = await searchGoogleBooks('author', 'Jane Doe');
        
        expect(axiosGetSpy).toHaveBeenCalledWith('https://www.googleapis.com/books/v1/volumes?q=inauthor%3A%22Jane%20Doe%22');
        expect(response).toEqual([{title: 'Harry Potter'}, {title: 'Harry Potter 2'}]);
    });
});

describe('displaySearchResults', () => {
    beforeEach(() => {
        //set up DOM
        $apiSearchResults = $('<div class="api-search-results"></div>').appendTo('body');
    });

    afterEach(() => {
        //clean up DOM
        $apiSearchResults.remove();
    });

    it('correctly displays search results', () => {
        const response = [
            {
                id: "1234",
                volumeInfo: {
                    imageLinks: {smallThumbnail: "http://www.google.com"},
                    title: 'A Night of Wings and Starlight',
                    authors: ['Alexis L. Menard'],
                    publishedDate: '2022'
                }
            },
            {
                id: "5678",
                volumeInfo: {
                    title: 'Black AF History', 
                    subtitle: 'The Un-Whitewashed Story of America', 
                    authors: ['Michael Harriot', 'China Mieville'],
                    publisher: 'HarperCollins', 
                    publishedDate: '2025'
                }
            },
            {
                id: "91011", 
                volumeInfo: {
                    imageLinks: {smallThumbnail: "http://books.google.com/books/publisher/content?id=at_gEAAAQBAJ"},
                    title: 'Stolen', 
                    authors: ['Ann-Helen Laestadius'],
                    publisher: 'Bloomsbury'
                }
            }
        ];

        displaySearchResults(response);
        console.log($apiSearchResults);
        expect($apiSearchResults.html()).toContain(`<div class="row border"><div class="col-4"><img src="http://www.google.com"></div><div class="col"><div><a href="/books/1234">A Night of Wings and Starlight</a></div><div>Alexis L. Menard</div><div>2022</div></div>`);
        expect($apiSearchResults.html()).toContain(`<div class="row border"><div class="col-4"></div><div class="col"><div><a href="/books/5678">Black AF History: The Un-Whitewashed Story of America</a></div><div>Michael Harriot</div><div>HarperCollins, 2025</div></div></div>`);
        expect($apiSearchResults.html()).toContain(`<div class="row border"><div class="col-4"><img src="http://books.google.com/books/publisher/content?id=at_gEAAAQBAJ"></div><div class="col"><div><a href="/books/91011">Stolen</a></div><div>Ann-Helen Laestadius</div><div>Bloomsbury</div></div></div>`);
    });
});

describe('assign to challenge event handler', () => {
    let axiosPostSpy;
    beforeEach(() => {
        //create spy
        axiosPostSpy = spyOn(axios, 'post').and.returnValue(Promise.resolve({success: true}));

        //set up DOM
        $assignToChallengeForm = $('<form class="assign-to-challenge-form"><span class="error-span">Error Message Here</span></form>');
        $challengesField = $('<select name="challenges" id="challenges"><option value=1></option></select>');
        $assignChallengeButton = $('<button class="assign-challenge-button">Assign to Challenge</button>');

        //attach event handler
        $assignChallengeButton.on('click', async function(event){
            event.preventDefault();
            $assignToChallengeForm.find('.error-span').remove();
            //get the challenge being assigned to
            const challenge_id = $challengesField.val();
            //get the userbook_id
            currentURL = "http://127.0.0.1:5000/users_books/64";
            const userbook_id = parseInt(currentURL.substring(currentURL.lastIndexOf('/') + 1));
            //send the data
            const data = {'challenge_id': challenge_id};
            const response = await axios.post(`/api/users_books/${userbook_id}/assign`, data);
            if (response.data['success']){
                $errorSpan = $('<span class="text-sm text-success error-span">Book assigned to challenge</span>');
                $assignToChallengeForm.append($errorSpan);
            }
            if (response.data['error']){
                $errorSpan = $('<span class="text-sm text-danger error-span">This book is already assigned to this challenge.</span>');
                $assignToChallengeForm.append($errorSpan);
            }
        });
    });

    afterEach(() => {
        //clean up DOM
        $assignToChallengeForm.remove();
        $challengesField.remove();
        $assignChallengeButton.remove();
    });

    it('collects the correct data and sends it via axios', async () => {
        $challengesField.val(1);

        const event = $.Event('click');
        await $assignChallengeButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(axiosPostSpy).toHaveBeenCalledWith('/api/users_books/64/assign', {'challenge_id': 1});
        expect($assignToChallengeForm.find('.error-span').length).toEqual(1);
        expect($assignToChallengeForm.find('.error-span').text()).toEqual('Book assigned to challenge')
    });

    it('returns the correct message if error is returned', async () => {
        $challengesField.val(1);
        axiosPostSpy.and.returnValue(Promise.resolve({error: true}));

        const event = $.Event('click');
        await $assignChallengeButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(axiosPostSpy).toHaveBeenCalled();
        expect($assignToChallengeForm.find('error-span').length).toEqual(1);
        expect($assignToChallengeForm.find('.error-span').text()).toEqual('This book is already assigned to this challenge.')
    });
});

describe('remove from book challenge event handler', () => {});