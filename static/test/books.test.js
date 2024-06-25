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
                id: 1234,
                volumeInfo: {
                    imageLinks: {smallThumbnail: "http://www.google.com"},
                    title: 'A Night of Wings and Starlight',
                    authors: ['Alexis L. Menard'],
                    publishedDate: '2022'
                }
            },
            {
                id: 5678,
                volumeInfo: {
                    title: 'Black AF History', 
                    subtitle: 'The Un-Whitewashed Story of America', 
                    authors: ['Michael Harriot', 'China Mieville'],
                    publisher: 'HarperCollins', 
                    publishedDate: '2025'
                }
            },
            {
                id: 91011, 
                volumeInfo: {
                    imageLinks: {smallThumbnail: "http://books.google.com/books/publisher/content?id=at_gEAAAQBAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE71oovDeOSaZbYqyDqpoIoIHe_7JM1DiAdYmhir0oA3nKz9fFtxY66HpmQ8MX63s8RRkXuM-pSptg8C5ufqVd3_Y0KvEZJL02OCUWd8cvR4LeAMj2iKqPbgOCwmil_uMWO91Vrfr&source=gbs_api" },
                    title: 'Stolen', 
                    authors: ['Ann-Helen Laestadius'],
                    publisher: 'Bloomsbury'
                }
            }
        ];

        const html = displaySearchResults(response);
        console.log(displaySearchResults('html is ', html));
        console.log('testing = ', response[0].volumeInfo.imageLinks);

        expect(html).toEqual('<div class="row border"><div class="col-4"><img src="http://www.google.com"></div><div class="col"><div><a href="/books/1234">A Night of Wings and Starlight</a></div><div>Alexis L. Menard</div><div>2022</div></div></div><div class="row border"><div class="col-4"></div><div class="col"><div><a href="/books/5678">Black AF History: The Un-Whitewashed Story of America</a></div><div>Michael Harriot</div><div>HarperCollins, 2025</div></div></div><div class="row border"><div class="col-4"><img src="http://books.google.com/books/publisher/content?id=at_gEAAAQBAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE71oovDeOSaZbYqyDqpoIoIHe_7JM1DiAdYmhir0oA3nKz9fFtxY66HpmQ8MX63s8RRkXuM-pSptg8C5ufqVd3_Y0KvEZJL02OCUWd8cvR4LeAMj2iKqPbgOCwmil_uMWO91Vrfr&source=gbs_api"></div><div class="col"><div><a href="/books/91011">Stolen</a></div><div>Ann-Helen Laestadius</div><div>Bloomsbury</div></div></div>');
    });
});

describe('assign to challenge event handler', () => {});

describe('remove from book challenge event handler', () => {});