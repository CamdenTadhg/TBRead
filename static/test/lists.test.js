describe('displayUserBooks', () => {
    beforeEach(() => {
        //set up DOM
        $userBookList = $('<tbody class="user-book-list">TESTING CLEAR</tbody>').appendTo('body');
        $table = $('<table class="book-list-table" id="tbrlistTable"><thead></thead></table>')

        //create spy
        fancyTableSpy = spyOn($table, 'fancyTable');
    });
    afterEach(() => {
        //clean up DOM
        $userBookList.remove();
    });
    it('creates and displays a table of list books', () => {
        const bookList = [
            {
                id: 5,
                title: 'Chlorine: A Novel',
                authors: 'Jade Song',
                publisher: 'HarperCollins',
                pub_date: '2023',
                pages: 256,
                cover: 'http://books.google.com/books/publisher/content?id=5k13EAAAQBAJ'
            },
            {
                id: 24,
                title: 'Chain Gang All Stars: A Novel', 
                authors: 'Nana Kwame Adjei-Brenyah',
                publisher: 'Knopf Doubleday Publishing Group', 
                pub_date: '2024', 
                pages: 432,
                cover: 'http://books.google.com/books/publisher/content?id=J07kEAAAQBAJ'
            }
        ];
        const currentURL = window.location.href;

        displayUserBooks(bookList);

        expect(fancyTableSpy).toHaveBeenCalled();
        expect($userBookList.children('tr').length).toEqual(2);
        expect($userBookList.html()).toContain(`<tr><td><img class="list-cover" src="http://books.google.com/books/publisher/content?id=5k13EAAAQBAJ"></td><td data-sortvalue="Chlorine: A Novel"><a href="/users_books/5">Chlorine: A Novel</a></td><td>Jade Song</td><td>HarperCollins</td><td>2023</td><td>256</td><td><form method="POST" action="/users_books/5/delete"><button class="btn btn-danger"><i class="fa-solid fa-trash-can"></i></button></form></td>`);
        if (currentURL.includes('dnf')){
            expect($userBookList.html()).toContain('<td><form method="POST" action="/users_books/5/transfer/TBR"><button class="btn btn-info">TBR</button></form></td>');
            expect($userBookList.html()).toContain('<td><form method="POST" action="/users_books/5/transfer/Complete"><button class="btn btn-info">Complete</button></form></td>');
        }
        if (currentURL.includes('complete')){
            expect($userBookList.html()).toContain('<td><form method="POST" action="/users_books/5/transfer/DNF"><button class="btn btn-info">DNF</button></form></td>`');
            expect($userBookList.html()).toContain('<td><form method="POST" action="/users_books/5/transfer/TBR"><button class="btn btn-info">TBR</button></form></td>')
        }
        if (currentURL.includes('tbr')){
            expect($userBookList.html()).toContain('<td><form method="POST" action="/users_books/5/transfer/DNF"><button class="btn btn-info">DNF</button></form></td>');
            expect($userBookList.html()).toContain('<td><form method="POST" action="/users_books/5/transfer/Complete"><button class="btn btn-info">Complete</button></form></td>');
        }
    });
});

describe('userBooksOnStart', () => {
    let getUserBooksSpy, displayUserBooksSpy
    beforeEach(() => {
        //create spies
        getUserBooksSpy = spyOn(UserBookList, 'getUserBooks').and.returnValue(Promise.resolve([{title: 'Harry Potter'}, {title: 'Harry Potter 2'}]));
        displayUserBooksSpy = jasmine.createSpy('displayUserBooks');
        window.displayUserBooks = displayUserBooksSpy;
    });
    afterEach(() => {
        window.displayUserBooks = displayUserBooks;
    });
    it('runs functions to display list books', async () => {
        g_user_id = 1;
        type = 'dnf';

        await userBooksOnStart();

        expect(getUserBooksSpy).toHaveBeenCalledWith(1, 'dnf');
        expect(displayUserBooksSpy).toHaveBeenCalledWith([{title: 'Harry Potter'}, {title: 'Harry Potter 2'}]);
    });
});

describe('page load handler', () => {
    let userBooksOnStartSpy;
    beforeEach(() => {
        //create spy
        userBooksOnStartSpy = jasmine.createSpy('userBooksOnStart');
        window.userBooksOnStart = userBooksOnStartSpy;

        //attach event handler
        $(document).ready(function(){
            userBooksOnStart();
        });
    });
    afterEach(() => {
        window.userBooksOnStart = userBooksOnStart;
    });
    it('should call userBooksOnStart on page load', function(done) {
        // Mock DOMContentLoaded event
        $(document).ready(function() {
            expect(window.userBooksOnStart).toHaveBeenCalled();
            done();
        });

        // Trigger the DOMContentLoaded event
        const event = new Event('DOMContentLoaded');
        document.dispatchEvent(event);
    });
});