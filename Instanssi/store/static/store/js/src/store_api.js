
/**
 * Perform an asynchronous HTTP request to a specific method and path,
 * optionally passing some data (not supported for GET requests).
 * @param {string} method - HTTP method, e.g. 'GET'
 * @param {string} path - URL or path to request
 * @param {Object} [data] - Data to pass in the request (encoded into JSON)
 * @returns {Promise.Object} - Result
 */
export function storeXHR(method, path, data) {
    return new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        xhr.onload = function () {
            if(xhr.status >= 200 && xhr.status < 300) {
                // tolerate empty response (technically, 204 no content should be used...)
                let response = xhr.responseText;
                resolve((response && response.length) ? JSON.parse(xhr.responseText) : null);
            } else {
                xhr.onerror();
            }
        };
        xhr.onerror = function () {
            reject(xhr.responseText ? JSON.parse(xhr.responseText) : null);
        };
        xhr.open(method, path);
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(data ? JSON.stringify(data) : null);
    });
}
