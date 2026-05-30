const fs = require('fs');
const text = fs.readFileSync('styles.css', 'utf8');

const doubleQuotes = text.match(/"/g) || [];
const singleQuotes = text.match(/'/g) || [];

console.log('Double quotes:', doubleQuotes.length);
console.log('Single quotes:', singleQuotes.length);

if (doubleQuotes.length % 2 !== 0) {
    console.log('Odd number of double quotes! Fixing by replacing all " with \'');
    const fixed = text.replace(/"/g, "'");
    fs.writeFileSync('styles.css', fixed, 'utf8');
} else if (singleQuotes.length % 2 !== 0) {
    console.log('Odd number of single quotes!');
} else {
    console.log('Quotes are balanced.');
}
