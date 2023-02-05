module.exports = {
    moduleNameMapper: {
        "^vue$": "<rootDir>/static/libs/vue/vue.js"
    },
    transform: {
        '\\.html$': '<rootDir>/jest.transform.file.js',
        '\\.(js|jsx)$': 'babel-jest'
    }
}
