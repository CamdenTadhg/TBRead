describe('UserBook', () => {
    it('should correctly assign properties from the constructor', () => {
        const bookData = {
            id: 1,
            user_id: 1,
            book_id: 3,
            title: 'A Night of Wings and Starlight',
            authors: ['Alexis L. Menard'],
            publisher: 'CITY OWL Press', 
            pub_date: 2022,
            pages: 258,
            age_category: "Adult", 
            thumbnail: 'http://books.google.com/books/content?id=9nPrzgEACAAJ',
            notes: '',
            script: ''
        }

        const userBook = new UserBook(bookData);

        expect(userBook.id).toEqual(1);
        expect(userBook.user_id).toEqual(1);
        expect(userBook.book_id).toEqual(3);
        expect(userBook.title).toEqual('A Night of Wings and Starlight');
        expect(userBook.authors).toEqual(['Alexis L. Menard']);
        expect(userBook.publisher).toEqual('CITY OWL Press');
        expect(userBook.pub_date).toEqual(2022);
        expect(userBook.description).toEqual('Breaking the curse will risk her heart');
        expect(userBook.isbn).toEqual(9781648981708);
        expect(userBook.page_count).toEqual(258);
        expect(userBook.age_category).toEqual('Adult');
        expect(userBook.thumbnail).toEqual('http://books.google.com/books/content?id=9nPrzgEACAAJ');
        expect(userBook.notes).toEqual('');
        expect(userBook.script).toEqual('');
    });
});

describe('UserBookList', () => {
    it('should correctly assign properties from the constructor', () => {
        const bookListData = [
            {
                id: 1,
                user_id: 1,
                book_id: 3,
                title: 'A Night of Wings and Starlight',
                authors: ['Alexis L. Menard'],
                publisher: 'CITY OWL Press', 
                pub_date: 2022,
                description: 'Breaking the curse will risk her heart',
                isbn: 9781648981708,
                page_count: 258,
                age_category: "Adult", 
                thumbnail: 'http://books.google.com/books/content?id=9nPrzgEACAAJ',
                notes: '',
                script: ''
            },
            {
                id: 2,
                user_id: 1,
                book_id: 5,
                title: 'Archangels of Funk', 
                authors: ['Andrea Hairston'],
                publisher: 'Tor Publishing Group', 
                pub_date: '2024',
                thumbnail: 'http://books.google.com/books/publisher/content?id=YszREAAAQBAJ'
            }
        ]
    });
    it('should pull full list of books and return them as a UserBookList', () => {});
});

describe('Challenge', () => {
    it('should correctly assign properties from the constructor', () => {});
});

describe('ChallengeList', () => {
    it('should correctly assign properties from the constructor', () => {});
    it('should pull a list of all challenges and return them as a ChallengeList', () => {});
    it("should pull a list of user's challenges and return them as a ChallengeList", () => {});
});