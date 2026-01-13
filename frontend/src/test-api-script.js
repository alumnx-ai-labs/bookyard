import { booksAPI, healthAPI } from './services/api.js';

console.log('Testing API connectivity...');

async function test() {
    try {
        console.log('Checking health...');
        const health = await healthAPI.check();
        console.log('Health Check:', health);

        console.log('Fetching books...');
        const books = await booksAPI.list();
        console.log('Books found:', books.length);
        if (books.length > 0) {
            console.log('First book:', books[0]);
        }
    } catch (error) {
        console.error('API Test Failed:', error.message);
        if (error.response) {
            console.error('Response Status:', error.response.status);
            console.error('Response Data:', error.response.data);
        }
    }
}

test();
