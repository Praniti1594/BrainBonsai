/**
 * SearchManager centralizes topic discovery and result assignment logic.
 */
class SearchManager {
    constructor(game, apiBaseUrl) {
        this.game = game;
        this.apiBaseUrl = apiBaseUrl;
        this.reset();
    }

    reset() {
        this.searchResults = [];
        this.originalQuery = null;
        this.usedTitles = new Set();
    }

    getOriginalQuery() {
        return this.originalQuery;
    }

    getInitialResults() {
        return this.searchResults;
    }

    async fetchInitialResults(query) {
        console.log('SearchManager: fetching search results for:', query);
        this.originalQuery = query;

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            console.log('SearchManager: initial search status:', response.status);
            const data = await response.json();
            console.log('SearchManager: initial search payload:', data);

            if (data.results) {
                this.searchResults = data.results;
                this.game.updateStatus(`Found ${data.results.length} topics! Use study tool to explore.`);
                return data.results;
            }
        } catch (error) {
            console.error('SearchManager: initial search failed', error);
            this.game.updateStatus('Search failed. Please try again.');
        }

        this.searchResults = [];
        return [];
    }

    assignInitialResults(branches) {
        if (!branches || branches.length === 0) {
            return;
        }

        if (!this.searchResults || this.searchResults.length === 0) {
            console.log('SearchManager: no initial results available to assign.');
            return;
        }

        branches.forEach((branch, index) => {
            const result = this.searchResults[index];
            if (!result) {
                return;
            }

            const sanitized = { ...result };
            delete sanitized.url;
            branch.searchResult = sanitized;

            const title = sanitized.title?.toLowerCase();
            if (title) {
                this.usedTitles.add(title);
            }

            console.log(`SearchManager: assigned initial result ${index} to branch:`, sanitized.title);
        });
    }

    async assignResultsToBranches(parentNode, newBranches) {
        if (!newBranches || newBranches.length === 0) {
            return;
        }

        const searchTopic = parentNode?.searchResult?.title || this.originalQuery;

        if (!searchTopic) {
            console.log('SearchManager: no search topic available for branch expansion.');
            return;
        }

        const researchQuery = `deep research on ${searchTopic} in the context of ${this.originalQuery}`;
        console.log(`SearchManager: fetching child results with query "${researchQuery}" for ${newBranches.length} branches.`);

        try {
            let collected = [];
            let attempts = 0;
            const maxAttempts = 10;

            while (collected.length < newBranches.length && attempts < maxAttempts) {
                const negativePrompts = collected.map(result => result.title);
                const response = await fetch(`${this.apiBaseUrl}/api/web-search`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: researchQuery,
                        count: Math.max(5, newBranches.length - collected.length + 2),
                        negative_prompts: negativePrompts
                    })
                });

                const data = await response.json();
                console.log(`SearchManager: attempt ${attempts + 1} results:`, data);

                if (data.results && data.results.length > 0) {
                    const unique = this.filterDuplicateResults(data.results);
                    collected = this.filterDuplicateResults([...collected, ...unique]);
                }

                attempts++;
            }

            console.log('SearchManager: final unique results:', collected);

            newBranches.forEach((branch, index) => {
                if (!collected[index]) {
                    console.warn(`SearchManager: no result available for branch index ${index}`);
                    return;
                }

                branch.searchResult = collected[index];

                const title = collected[index].title?.toLowerCase();
                if (title) {
                    this.usedTitles.add(title);
                }

                console.log(`SearchManager: assigned result to branch ${index}:`, collected[index].title);
            });

            const assignedCount = Math.min(collected.length, newBranches.length);
            if (attempts > 1) {
                this.game.updateStatus(`Found ${assignedCount} unique web search results after ${attempts} attempts with negative prompts!`);
            } else {
                this.game.updateStatus(`Found ${assignedCount} unique web search results for new branches!`);
            }
        } catch (error) {
            console.error('SearchManager: child search failed', error);
            this.game.updateStatus('Web search failed. Branches created without search results.');
        }
    }

    filterDuplicateResults(results) {
        const unique = [];
        const seen = new Set();

        results.forEach(result => {
            const titleLower = result.title?.toLowerCase();
            if (!titleLower) {
                return;
            }

            if (seen.has(titleLower) || this.usedTitles.has(titleLower)) {
                return;
            }

            seen.add(titleLower);
            unique.push(result);
        });

        return unique;
    }
}
