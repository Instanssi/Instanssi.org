module.exports = {
    moduleNameMapper: {
        "^vue$": "<rootDir>../backend/Instanssi/static/libs/vue/vue.js"
    },
    transform: {
        '\\.html$': '<rootDir>/jest.transform.file.js',
        '\\.(js|jsx)$': 'babel-jest'
    },
    testURL: "http://localhost/"
}
