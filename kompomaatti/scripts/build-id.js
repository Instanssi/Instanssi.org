import cp from 'node:child_process';

function getBuildId() {
    const gitClean = checkGitClean();
    const gitHash = checkGitHash().slice(0, 7);
    const timestamp = Math.floor(new Date().valueOf() / 1000);

    return `git-${gitClean ? '' : 'uc-'}${gitHash}-${timestamp}`;
}

/**
 * Check if the current Git repository is clean.
 * @returns {boolean} - true if repository is untouched
 */
function checkGitClean() {
    try {
        // git diff-index --quiet returns 1 if there were differences:
        // https://git-scm.com/docs/git-diff-index
        // execSync throws if the command exits with nonzero:
        // https://nodejs.org/api/child_process.html
        cp.execSync('git diff-index --quiet --cached HEAD --');
    } catch(err) {
        return false;
    }
    return true;
}

/**
 * Get the current Git repository's HEAD hash.
 * @returns {string} - Current Git HEAD.
 */
function checkGitHash() {
    try {
        return cp.execSync('git rev-parse HEAD');
    } catch(err) {
        return 'unknown';
    }
}


export default getBuildId;
