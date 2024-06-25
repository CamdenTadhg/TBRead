describe('UserBook', () => {
    it('should correctly assign properties from the constructor', () => {
        const bookData = {
            id: 1,
            title: 'A Night of Wings and Starlight',
            authors: ['Alexis L. Menard'],
            publisher: 'CITY OWL Press', 
            pub_date: 2022,
            pages: 258,
            cover: 'http://books.google.com/books/content?id=9nPrzgEACAAJ',
        }

        const userBook = new UserBook(bookData);

        expect(userBook.id).toEqual(1);
        expect(userBook.title).toEqual('A Night of Wings and Starlight');
        expect(userBook.authors).toEqual(['Alexis L. Menard']);
        expect(userBook.publisher).toEqual('CITY OWL Press');
        expect(userBook.pub_date).toEqual(2022);
        expect(userBook.pages).toEqual(258);
        expect(userBook.cover).toEqual('http://books.google.com/books/content?id=9nPrzgEACAAJ');
    });
});

describe('UserBookList', () => {
    it('should correctly assign properties from the constructor', () => {
        const bookListData = [
            {
                id: 1,
                title: 'A Night of Wings and Starlight',
                authors: ['Alexis L. Menard'],
                publisher: 'CITY OWL Press', 
                pub_date: 2022,
                pages: 258,
                cover: 'http://books.google.com/books/content?id=9nPrzgEACAAJ',
            },
            {
                id: 2,
                title: 'Archangels of Funk', 
                authors: ['Andrea Hairston'], 
                publisher: 'Tor Publishing Group',
                pub_date: 2024,
                pages: 524,
                cover: 'http://books.google.com/books/publisher/content?id=YszREAAAQBAJ'
            }
        ];

        const userBookList = new UserBookList(bookListData);

        expect(userBookList.userBooks.length).toEqual(2);
        expect(userBookList.userBooks[0].title).toEqual('A Night of Wings and Starlight');
        expect(userBookList.userBooks[1].title).toEqual('Archangels of Funk');
    });
    it('should pull full list of books and return them as a UserBookList', async () => {
        const mockData = [
            {
                id: 5,
                title: 'Chlorine: A Novel',
                authors: ['Jade Song'],
                publisher: 'HarperCollins',
                pub_date: '2023',
                pages: 256,
                cover: 'http://books.google.com/books/publisher/content?id=5k13EAAAQBAJ'
            },
            {
                id: 24,
                title: 'Chain Gang All Stars: A Novel', 
                authors: ['Nana Kwame Adjei-Brenyah'],
                publisher: 'Knopf Doubleday Publishing Group', 
                pub_date: '2024', 
                pages: 432,
                cover: 'http://books.google.com/books/publisher/content?id=J07kEAAAQBAJ'
            }
        ];
        const user_id = 1;
        const list_type = 'tbr';
        const axiosGetSpy = spyOn(axios, 'get').and.returnValue(Promise.resolve({data: mockData}));

        const response = await UserBookList.getUserBooks(user_id, list_type);

        expect(axiosGetSpy).toHaveBeenCalledWith('/api/1/lists/tbr');
        expect(response).toEqual(mockData);
    });
});

describe('Challenge', () => {
    it('should correctly assign properties from the constructor', () => {
        const challengeData = {
            id: 1, 
            name: 'Marginalized Authors', 
            num_books: 100,
            description: 'test description'
        };

        const challenge = new Challenge(challengeData);

        expect(challenge.id).toEqual(1);
        expect(challenge.name).toEqual('Marginalized Authors');
        expect(challenge.num_books).toEqual(100);
        expect(challenge.description).toEqual('test description');
    });
});

describe('ChallengeList', () => {
    it('should correctly assign properties from the constructor', () => {
        const challengeListData = [
            {
                id: 1,
                name: 'Marginalized Authors', 
                num_books: 100,
                description: 'test description'
            },
            {
                id: 2,
                name: '50 Books', 
                num_books: 50,
                description: 'test description 2'
            }
        ];

        const challengeList = new ChallengeList(challengeListData);

        expect(challengeList.challenges.length).toEqual(2);
        expect(challengeList.challenges[0].name).toEqual('Marginalized Authors');
        expect(challengeList.challenges[1].num_books).toEqual(50);
    });
    it('should pull a list of all challenges and return them as a ChallengeList', async () => {
        const mockChallengeData = [
            {
                id: 1,
                name: 'Marginalized Authors', 
                num_books: 100,
                description: 'test description'
            },
            {
                id: 2,
                name: '50 Books', 
                num_books: 50,
                description: 'test description 2'
            }
        ];
        const axiosGetSpy = spyOn(axios, 'get').and.returnValue(Promise.resolve({data: mockChallengeData}));

        const response = await ChallengeList.getChallenges();

        expect(axiosGetSpy).toHaveBeenCalledWith('/api/challenges');
        expect(response.length).toEqual(2);
        expect(response).toEqual(mockChallengeData);
    });
    it("should pull a list of user's challenges and return them as a ChallengeList", async () => {
        const mockUserChallengeData = [
            {
                id: 3,
                name: 'Award Winners', 
                num_books: 12,
                description: 'test description 3'
            },
            {
                id: 4,
                name: '100 Books', 
                num_books: 100,
                description: 'test description 4'
            }
        ];
        const axiosGetSpy = spyOn(axios, 'get').and.returnValue(Promise.resolve({data: mockUserChallengeData}));

        const response = await ChallengeList.getYourChallenges();

        expect(axiosGetSpy).toHaveBeenCalledWith('/api/yourchallenges');
        expect(response.length).toEqual(2);
        expect(response).toEqual(mockUserChallengeData);
    });
});