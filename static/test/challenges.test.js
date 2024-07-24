describe('displayChallenges', () => {
    let currentURL = window.location.href;
    beforeEach(() => {
        //set up DOM
        $challengesList = $('<tbody class="challenge-list">TEST CLEARING</tbody>').appendTo('body');
    });
    afterEach(() => {
        //clean up DOM
        $challengesList.remove();
    });
    if (!currentURL.includes('user')){
        it('displays a table of challenges with appropriate edit links', () => {
            user_id = 1;
            const challengeListData = [
                {
                    id: 1,
                    creator_id: 1,
                    name: 'Marginalized Authors', 
                    num_books: 100,
                    description: 'test description'
                },
                {
                    id: 2,
                    creator_id: 2,
                    name: '50 Books', 
                    num_books: 50,
                    description: 'test description 2'
                }
            ];

            displayChallenges(challengeListData);

            expect($challengesList.html()).toContain('<tr><td data-sortvalue="Marginalized Authors"><a href="/challenges/1">Marginalized Authors</a></td><td>100</td><td>test description</td><td><form method="POST" action="/challenges/join/1"><button class="btn btn-primary join">Join Challenge</button></form></td></tr>');
            expect($challengesList.html()).toContain('<tr><td data-sortvalue="50 Books">50 Books</td><td>50</td><td>test description 2</td><td><form method="POST" action="/challenges/join/2"><button class="btn btn-primary join">Join Challenge</button></form></td></tr>');
        });
    }
    if (currentURL.includes('user')){
        it('displays a table of user challenges', () => {
            user_id = 1;
            const challengeListData = [
                {
                    id: 1,
                    creator_id: 1,
                    name: 'Marginalized Authors', 
                    num_books: 100,
                    description: 'test description',
                    start_date: '1/1/2024',
                    end_date: undefined
                },
                {
                    id: 2,
                    creator_id: 2,
                    name: '50 Books', 
                    num_books: 50,
                    description: 'test description 2',
                    start_date: '1/1/2024',
                    end_date: '12/31/2024'
                }
            ];

            displayChallenges(challengeListData);

            expect($challengesList.html()).toContain('<tr><td data-sortvalue="Marginalized Authors"><a href="/users/1/challenges/1">Marginalized Authors</a></td><td>100</td><td>test description</td><td>1/1/2024</td><td></td><td><form method="POST" action="/challenges/leave/1"><button class="btn btn-danger leave ">Leave Challenge</button></form></td></tr>');
        });
    }
});

describe('challengesOnStart', () => {
    let currentURL = window.location.href;
    let getYourChallengesSpy, getChallengesSpy, displayChallengesSpy
    beforeEach(() => {
        getYourChallengesSpy = spyOn(ChallengeList, 'getYourChallenges').and.returnValue([{name: 'Test Challenge 1'}, {name: 'Test Challenge 2'}]);
        getChallengesSpy = spyOn(ChallengeList, 'getChallenges').and.returnValue([{name: 'Test Challenge 3'}, {name: 'Test Challenge 4'}]);
        displayChallengesSpy = jasmine.createSpy('displayChallenges');
        window.displayChallenges = displayChallengesSpy;
    });
    afterEach(() => {
        window.displayChallenges = displayChallenges;
    });
    if (!currentURL.includes('user')){
        it('runs the necessary functions to get a list of challenges', async () => {
            await challengesOnStart();

            expect(getChallengesSpy).toHaveBeenCalled();
            expect(displayChallengesSpy).toHaveBeenCalledWith([{name: 'Test Challenge 3'}, {name: 'Test Challenge 4'}]);
        });
    };
    if (currentURL.includes('user')){
        it('runs the necessary functions to get a list of user challenges', async () => {
            await challengesOnStart();

            expect(getYourChallengesSpy).toHaveBeenCalled();
            expect(displayChallengesSpy).toHaveBeenCalledWith([{name: 'Test Challenge 1'}, {name: 'Test Challenge 2'}])
        });
    }
});

describe('activeTab challenges', () => {
    let getCurrentURLSpy;
    beforeEach(() => {
        //create spy
        getCurrentURLSpy = jasmine.createSpy('getCurrentURL').and.returnValue('http://tb-read/challenges');
        window.getCurrentURL = getCurrentURLSpy;
        //set up DOM
        $allTab = $('<a href="/challenges" class="btn btn-secondary mt-2 tab all-tab">All Challenges</a>').appendTo('body');
        $yourTab = $('<a href="users/1/challenges" class="btn btn-primary mt-2 tab your-tab">Your Challenges</a>').appendTo('body');
    });

    afterEach(() => {
        //clean up DOM
        $allTab.remove();
        $yourTab.remove();

        window.getCurrentURL = getCurrentURL
    });

    it('changes tabs appropriately to signify which tab is live', () => {
        activeTab();
        allClassList = $allTab.attr('class');
        yourClassList = $yourTab.attr('class');
        expect(getCurrentURLSpy).toHaveBeenCalled();
        expect(yourClassList).toContain('btn-secondary');
        expect(yourClassList).not.toContain('btn-primary');
        expect(allClassList).toContain('btn-primary');
        expect(allClassList).not.toContain('btn-secondary');
    });
});

describe('page load event handler', () => {
    let challengesOnStartSpy, activeTabSpy;
    beforeEach(() => {
        //create spy
        challengesOnStartSpy = jasmine.createSpy('challengesOnStart');
        window.challengesOnStart = challengesOnStartSpy;
        activeTabSpy = jasmine.createSpy('activeTab');
        window.activeTab = activeTabSpy;

        //attach event handler
        $(document).ready(function(){
            activeTab();
            challengesOnStart();
        });
    });
    afterEach(() => {
        window.challengesOnStart = challengesOnStart;
        window.activeTab = activeTab;
    });
    it('should call challengesOnStart on page load', function(done) {
        // Mock DOMContentLoaded event
        $(document).ready(function() {
            expect(window.challengesOnStart).toHaveBeenCalled();
            expect(window.activeTab).toHaveBeenCalled();
            done();
        });

        // Trigger the DOMContentLoaded event
        const event = new Event('DOMContentLoaded');
        document.dispatchEvent(event);
    });
});